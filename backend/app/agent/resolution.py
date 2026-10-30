from typing import Dict, Any
from app.agent.state import ITSupportState
from app.agent.tools.infra_tool import (
    execute_service_restart,
    execute_flush_db_pool,
    clear_cache
)
from app.agent.tools.ticket_tool import update_incident_record
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def resolution_node(state: ITSupportState) -> Dict[str, Any]:
    """Resolution Agent: Selects troubleshooting action, enforces Human-in-the-Loop for risky actions, and executes remediation."""
    service = state.get("affected_service", "api-gateway")
    root_cause = state.get("root_cause", "")
    
    # 1. Determine troubleshooting action accurately based on service & fault
    if "order-db" in service or ("database" in root_cause.lower() and "pool" in root_cause.lower()):
        target_service = "order-db"
        action_type = "flush_connection_pool"
        is_risky = True
        risk_justification = "Flushing database pool terminates idle worker sessions and resets connection limits. Human sign-off required to prevent active query aborts."
        proposed_action = f"execute_flush_db_pool(database_name='{target_service}')"
    elif "api-gateway" in service or "500" in root_cause or "deadlock" in root_cause.lower():
        target_service = "api-gateway"
        action_type = "restart_service"
        is_risky = True
        risk_justification = f"Restarting service '{target_service}' recycles worker threads and clears deadlock sockets. Brief 5-10s packet drop may occur. Requires human authorization."
        proposed_action = f"execute_service_restart(service_name='{target_service}')"
    elif "auth-service" in service or "jwks" in root_cause.lower():
        target_service = "auth-service"
        action_type = "restart_service"
        is_risky = True
        risk_justification = f"Restarting '{target_service}' forces re-fetching of latest JWKS keys. Requires human authorization."
        proposed_action = f"execute_service_restart(service_name='{target_service}')"
    else:
        target_service = service
        action_type = "clear_cache"
        is_risky = False
        risk_justification = "Low risk cache purge."
        proposed_action = f"clear_cache(service_name='{target_service}')"

    # 2. Check Human Approval Gate
    approval_status = state.get("human_approval_status")
    
    db = SessionLocal()
    try:
        if is_risky and approval_status != "APPROVED":
            thought = f"Identified remediation: '{proposed_action}'. Action is flagged as HIGH RISK: {risk_justification}. Halting execution and awaiting Human-in-the-Loop authorization."
            
            step = AgentStepLog(
                incident_id=state["incident_id"],
                node_name="resolution_human_gate",
                status="AWAITING_APPROVAL",
                thought_summary=thought,
                tool_name="human_approval_interrupter",
                tool_input={"proposed_action": proposed_action, "risk_level": "HIGH", "risk_justification": risk_justification},
                tool_output={"status": "AWAITING_APPROVAL"}
            )
            db.add(step)
            
            update_incident_record(
                db=db,
                incident_id=state["incident_id"],
                status="AWAITING_APPROVAL",
                proposed_action=proposed_action,
                action_risk_level="HIGH",
                human_approval_required=True,
                human_approval_status="PENDING"
            )
            db.commit()
            
            return {
                "proposed_action": proposed_action,
                "action_type": action_type,
                "target_service": target_service,
                "is_risky": True,
                "risk_justification": risk_justification,
                "human_approval_required": True,
                "human_approval_status": "PENDING",
                "action_executed": False,
                "current_node": "resolution_paused"
            }

        # If rejected by human
        if approval_status == "REJECTED":
            feedback = state.get("human_feedback", "Operator denied execution.")
            thought = f"Action '{proposed_action}' was REJECTED by Human Operator. Feedback: '{feedback}'. Aborting automated execution."
            
            step = AgentStepLog(
                incident_id=state["incident_id"],
                node_name="resolution",
                status="ACTION_REJECTED",
                thought_summary=thought,
                tool_name="human_feedback_handler",
                tool_input={"human_feedback": feedback},
                tool_output={"action_executed": False, "status": "ESCALATED"}
            )
            db.add(step)
            
            update_incident_record(
                db=db,
                incident_id=state["incident_id"],
                status="ESCALATED",
                human_approval_status="REJECTED",
                execution_result=f"Execution cancelled: {feedback}"
            )
            db.commit()
            
            return {
                "action_executed": False,
                "execution_result": f"Operator rejected action: {feedback}",
                "is_resolved": False,
                "verified": True,
                "current_node": "resolution_rejected"
            }

        # Action is either SAFE or APPROVED by human -> EXECUTE!
        exec_result: Dict[str, Any] = {}
        if action_type == "restart_service":
            exec_result = execute_service_restart(target_service)
        elif action_type == "flush_connection_pool":
            exec_result = execute_flush_db_pool(target_service)
        else:
            exec_result = clear_cache(target_service)

        result_str = f"Remediation executed successfully: {exec_result}"
        thought = f"Executing approved action '{proposed_action}' on '{target_service}'. Target system responded with success."

        step = AgentStepLog(
            incident_id=state["incident_id"],
            node_name="resolution",
            status="SUCCESS",
            thought_summary=thought,
            tool_name=action_type,
            tool_input={"service": target_service, "action": proposed_action},
            tool_output=exec_result
        )
        db.add(step)
        
        update_incident_record(
            db=db,
            incident_id=state["incident_id"],
            status="VERIFYING",
            proposed_action=proposed_action,
            human_approval_status=approval_status or "AUTO_APPROVED",
            execution_result=result_str
        )
        db.commit()
    finally:
        db.close()

    return {
        "proposed_action": proposed_action,
        "action_type": action_type,
        "target_service": target_service,
        "is_risky": is_risky,
        "action_executed": True,
        "execution_result": result_str,
        "current_node": "resolution"
    }
