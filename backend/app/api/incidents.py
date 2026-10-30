from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from app.core.database import get_db
from app.models.incident import Incident
from app.models.audit import AgentStepLog
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentApprovalRequest
from app.schemas.agent import AgentStepLogResponse
from app.agent.runner import run_agent_for_incident, resume_agent_with_approval

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentResponse])
def list_incidents(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("", response_model=IncidentResponse)
def create_incident(
    req: IncidentCreate,
    background_tasks: BackgroundTasks,
    auto_trigger: bool = True,
    db: Session = Depends(get_db)
):
    ticket_num = f"INC-2026-{random.randint(200, 999)}"
    incident = Incident(
        ticket_number=ticket_num,
        title=req.title,
        description=req.description,
        reporter_email=req.reporter_email or "employee@enterprise.io",
        affected_service=req.affected_service,
        severity=req.severity or "P2_HIGH",
        status="OPEN"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    if auto_trigger:
        # Run agent
        run_agent_for_incident(db, incident.id)
        db.refresh(incident)

    return incident

@router.post("/{incident_id}/trigger-agent")
def trigger_agent(incident_id: int, db: Session = Depends(get_db)):
    res = run_agent_for_incident(db, incident_id)
    return res

@router.post("/{incident_id}/approve")
def handle_approval(
    incident_id: int,
    req: IncidentApprovalRequest,
    db: Session = Depends(get_db)
):
    res = resume_agent_with_approval(db, incident_id, req.approved, req.feedback)
    return res

@router.get("/{incident_id}/steps", response_model=List[AgentStepLogResponse])
def get_incident_steps(incident_id: int, db: Session = Depends(get_db)):
    steps = db.query(AgentStepLog).filter(AgentStepLog.incident_id == incident_id).order_by(AgentStepLog.created_at.asc()).all()
    return steps
