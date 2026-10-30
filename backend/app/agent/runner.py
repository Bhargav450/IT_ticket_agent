from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agent.graph import agent_graph
from app.agent.state import ITSupportState
from app.models.incident import Incident
from app.models.audit import AgentStepLog

def run_agent_for_incident(db: Session, incident_id: int) -> Dict[str, Any]:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}

    thread_config = {"configurable": {"thread_id": f"ticket_{incident_id}"}}

    initial_state: ITSupportState = {
        "incident_id": incident.id,
        "ticket_number": incident.ticket_number,
        "title": incident.title,
        "description": incident.description,
        "reporter_email": incident.reporter_email,
        "triaged": False,
        "knowledge_retrieved": False,
        "diagnosed": False,
        "action_executed": False,
        "verified": False,
        "category": incident.category or "",
        "severity": incident.severity or "P3_MEDIUM",
        "affected_service": incident.affected_service or "",
        "reflection_count": incident.reflection_count or 0,
        "max_reflections": 2,
        "human_approval_status": incident.human_approval_status
    }

    final_state = agent_graph.invoke(initial_state, thread_config)
    return {
        "status": "completed",
        "incident_id": incident_id,
        "current_node": final_state.get("current_node"),
        "is_resolved": final_state.get("is_resolved", False),
        "human_approval_required": final_state.get("human_approval_required", False),
        "human_approval_status": final_state.get("human_approval_status")
    }

def resume_agent_with_approval(db: Session, incident_id: int, approved: bool, feedback: Optional[str] = None) -> Dict[str, Any]:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}

    thread_config = {"configurable": {"thread_id": f"ticket_{incident_id}"}}

    updated_state: ITSupportState = {
        "incident_id": incident.id,
        "ticket_number": incident.ticket_number,
        "title": incident.title,
        "description": incident.description,
        "triaged": True,
        "knowledge_retrieved": True,
        "diagnosed": True,
        "action_executed": False,
        "verified": False,
        "rag_citations": incident.rag_sources or [],
        "affected_service": incident.affected_service or "api-gateway",
        "category": incident.category or "APPLICATION",
        "severity": incident.severity or "P1_CRITICAL",
        "root_cause": incident.root_cause_analysis or "",
        "proposed_action": incident.proposed_action or "",
        "human_approval_required": True,
        "human_approval_status": "APPROVED" if approved else "REJECTED",
        "human_feedback": feedback,
        "reflection_count": incident.reflection_count or 0,
        "max_reflections": 2
    }

    final_state = agent_graph.invoke(updated_state, thread_config)
    return {
        "status": "resumed_completed",
        "incident_id": incident_id,
        "is_resolved": final_state.get("is_resolved", False),
        "verification_status": final_state.get("verification_status")
    }
