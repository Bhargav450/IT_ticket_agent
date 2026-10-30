from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class AgentStepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    node_name: str
    status: str
    thought_summary: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Any] = None
    tool_output: Optional[Any] = None
    created_at: datetime

class ServiceStatusSchema(BaseModel):
    service_name: str
    status: str
    latency_ms: float
    error_rate_percent: float
    cpu_percent: float
    memory_percent: float
    active_connections: int
    last_restarted: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SimulatedFailureRequest(BaseModel):
    scenario: str
