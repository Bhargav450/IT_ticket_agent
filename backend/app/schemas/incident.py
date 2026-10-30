from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str
    description: str
    reporter_email: Optional[str] = "employee@enterprise.io"
    affected_service: Optional[str] = None
    severity: Optional[str] = "P3_MEDIUM"

class IncidentApprovalRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    title: str
    description: str
    status: str
    severity: str
    category: str
    affected_service: Optional[str] = None
    reporter_email: str
    assigned_agent: str
    root_cause_analysis: Optional[str] = None
    rag_sources: Optional[List[Any]] = []
    proposed_action: Optional[str] = None
    action_risk_level: Optional[str] = "LOW"
    human_approval_required: bool = False
    human_approval_status: Optional[str] = None
    human_feedback: Optional[str] = None
    execution_result: Optional[str] = None
    verification_status: Optional[str] = None
    verification_details: Optional[str] = None
    resolution_notes: Optional[str] = None
    reflection_count: int = 0
    resolution_time_seconds: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
