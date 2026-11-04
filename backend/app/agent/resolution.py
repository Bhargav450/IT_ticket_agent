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
    
    category = state.get("category", "APPLICATION")
    rag_context = "\n".join([c.get("excerpt", "") for c in state.get("rag_citations", [])])
    
    # Safe autonomous handling for general IT or policy inquiries
    if category == "GENERAL_IT" or service == "enterprise-it":
        action_type = "provide_guidance"
        target_service = "enterprise-it"
        is_risky = False
        risk_justification = "Informational support query; no infrastructure mutation needed."
        proposed_action = "provide_knowledge_guidance()"
    else:
        prompt = f"""
        You are an expert IT Incident Resolution Agent.
        Diagnosed Root Cause: {root_cause}
        Impacted Service: {service}
        Category: {category}
        Runbook context: {rag_context}

        Remediation Playbook Standards:
        - restart_service: recycles worker processes, clears socket deadlocks, forces re-fetching of expired JWT/JWKS keys. (HIGH RISK - interrupts active sessions, requires human sign-off)
        - flush_connection_pool: flushes database connections and kills idle sessions. (HIGH RISK - resets database slots)
        - clear_cache: purges temporary cache memory to release memory pressure. (LOW RISK - safe automated operation)

        Return strictly valid JSON:
        {{
          "action_type": "restart_service" | "flush_connection_pool" | "clear_cache",
          "target_service": "{service}",
          "is_risky": true | false,
          "risk_justification": "explanation of operational risk",
          "proposed_action": "command string"
        }}
        """
        
        from app.agent.llm_factory import llm_client
        plan = llm_client.generate_json(prompt)
        
        action_type = plan.get("action_type") or "restart_service"
        target_service = plan.get("target_service") or service
        is_risky = bool(plan.get("is_risky", True))
        risk_justification = plan.get("risk_justification", "Action evaluation completed by autonomous agent.")

        # Canonicalize executable action commands
        if action_type == "restart_service":
            is_risky = True
            proposed_action = f"execute_service_restart(service_name='{target_service}')"
        elif action_type == "flush_connection_pool":
            is_risky = True
            proposed_action = f"execute_flush_db_pool(database_name='{target_service}')"
        elif action_type == "clear_cache":
            is_risky = False
            proposed_action = f"clear_cache(service_name='{target_service}')"
        else:
            is_risky = True
            proposed_action = f"execute_service_restart(service_name='{target_service}')"

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
        elif action_type == "provide_guidance":
            exec_result = {
                "success": True, 
                "action": "documentation_policy_guidance_provided",
                "message": "Policy explanation provided. Employee guided to IT Exception Request portal."
            }
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
