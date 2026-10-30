from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class AgentStepLog(Base):
    __tablename__ = "agent_step_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, index=True, nullable=False)
    node_name = Column(String, nullable=False) # supervisor, triage, knowledge, diagnostic, resolution, human_gate, verification
    status = Column(String, default="SUCCESS") # RUNNING, SUCCESS, AWAITING_APPROVAL, FAILED
    thought_summary = Column(Text, nullable=True) # LLM / Agent reasoning
    tool_name = Column(String, nullable=True) # e.g. query_application_logs
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
