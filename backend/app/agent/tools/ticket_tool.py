from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.incident import Incident

def update_incident_record(
    db: Session,
    incident_id: int,
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    affected_service: Optional[str] = None,
    root_cause: Optional[str] = None,
    proposed_action: Optional[str] = None,
    action_risk_level: Optional[str] = None,
    human_approval_required: Optional[bool] = None,
    human_approval_status: Optional[str] = None,
    execution_result: Optional[str] = None,
    verification_status: Optional[str] = None,
    verification_details: Optional[str] = None,
    resolution_notes: Optional[str] = None,
    reflection_count: Optional[int] = None,
    rag_sources: Optional[list] = None
) -> Dict[str, Any]:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"success": False, "error": f"Incident {incident_id} not found"}

    if status:
        incident.status = status
        if status == "RESOLVED":
            incident.resolved_at = datetime.utcnow()
            incident.resolution_time_seconds = int((datetime.utcnow() - incident.created_at).total_seconds())
    if category is not None:
        incident.category = category
    if severity is not None:
        incident.severity = severity
    if affected_service is not None:
        incident.affected_service = affected_service
    if root_cause is not None:
        incident.root_cause_analysis = root_cause
    if proposed_action is not None:
        incident.proposed_action = proposed_action
    if action_risk_level is not None:
        incident.action_risk_level = action_risk_level
    if human_approval_required is not None:
        incident.human_approval_required = human_approval_required
    if human_approval_status is not None:
        incident.human_approval_status = human_approval_status
    if execution_result is not None:
        incident.execution_result = execution_result
    if verification_status is not None:
        incident.verification_status = verification_status
    if verification_details is not None:
        incident.verification_details = verification_details
    if resolution_notes is not None:
        incident.resolution_notes = resolution_notes
    if reflection_count is not None:
        incident.reflection_count = reflection_count
    if rag_sources is not None:
        incident.rag_sources = rag_sources

    db.commit()
    db.refresh(incident)
    return {"success": True, "incident_id": incident.id, "status": incident.status}
