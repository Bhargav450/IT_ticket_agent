from typing import Dict, Any, Literal
from app.agent.state import ITSupportState
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def supervisor_node(state: ITSupportState) -> Dict[str, Any]:
    """Supervisor Agent: Evaluates workflow milestones, coordinates specialized nodes, and directs state transitions."""
    current = state.get("current_node", "start")
    
    db = SessionLocal()
    try:
        step = AgentStepLog(
            incident_id=state["incident_id"],
            node_name="supervisor",
            status="SUCCESS",
            thought_summary=f"Supervisor coordinating workflow. Current node: '{current}'. Evaluating next optimal agent node.",
            tool_name="supervisor_orchestrator",
            tool_input={"state_summary": {"current_node": current, "is_resolved": state.get("is_resolved", False)}},
            tool_output={"next_decision": "routing"}
        )
        db.add(step)
        db.commit()
    finally:
        db.close()

    return {"current_node": "supervisor"}

def supervisor_router(state: ITSupportState) -> Literal["triage", "knowledge", "diagnostic", "resolution", "verification", "end"]:
    # 0. Terminal states: if already verified or ended
    if state.get("is_resolved") or state.get("verified"):
        return "end"
    
    # 1. Triage phase
    if not state.get("triaged"):
        return "triage"
    
    # 2. Knowledge / RAG phase
    if not state.get("knowledge_retrieved"):
        return "knowledge"
    
    # 3. Diagnostic phase
    if not state.get("diagnosed"):
        return "diagnostic"
    
    # 4. Resolution phase
    if not state.get("action_executed"):
        if state.get("human_approval_status") == "PENDING":
            if state.get("proposed_action"):
                return "end" # Checkpointed / paused waiting for human authorization
        return "resolution"
    
    # 5. Verification phase
    if not state.get("verified"):
        return "verification"
    
    return "end"
