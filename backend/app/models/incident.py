from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from datetime import datetime
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Status & Classification
    status = Column(String, default="OPEN", index=True) 
    # OPEN, TRIAGED, INVESTIGATING, AWAITING_APPROVAL, ACTION_APPROVED, ACTION_REJECTED, EXECUTING, VERIFYING, RESOLVED, ESCALATED
    severity = Column(String, default="P3_MEDIUM") # P1_CRITICAL, P2_HIGH, P3_MEDIUM, P4_LOW
    category = Column(String, default="APPLICATION") # APPLICATION, DATABASE, AUTHENTICATION, INFRASTRUCTURE, NETWORK
    affected_service = Column(String, nullable=True) # api-gateway, order-db, auth-service, etc.
    reporter_email = Column(String, default="employee@enterprise.io")
    assigned_agent = Column(String, default="Autonomous IT Support Agent")

    # Reasoning & RAG
    root_cause_analysis = Column(Text, nullable=True)
    rag_sources = Column(JSON, default=list) # List of runbook citations and excerpts
    
    # Resolution & Human-in-the-Loop
    proposed_action = Column(Text, nullable=True) # e.g. restart_service(service="api-gateway")
    action_risk_level = Column(String, default="LOW") # LOW, HIGH, CRITICAL
    human_approval_required = Column(Boolean, default=False)
    human_approval_status = Column(String, nullable=True) # PENDING, APPROVED, REJECTED
    human_feedback = Column(Text, nullable=True)
    execution_result = Column(Text, nullable=True)
    
    # Verification & Metrics
    verification_status = Column(String, nullable=True) # PENDING, VERIFIED_HEALTHY, VERIFICATION_FAILED
    verification_details = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    reflection_count = Column(Integer, default=0)
    resolution_time_seconds = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

