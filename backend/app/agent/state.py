from typing import TypedDict, List, Dict, Any, Optional

class ITSupportState(TypedDict, total=False):
    # Incident Identification
    incident_id: int
    ticket_number: str
    title: str
    description: str
    reporter_email: str
    
    # Phase Flags
    triaged: bool
    knowledge_retrieved: bool
    diagnosed: bool
    action_executed: bool
    verified: bool
    
    # Triage Classification
    category: str
    severity: str
    affected_service: str
    triage_reasoning: str
    
    # Knowledge / RAG & Memory
    rag_citations: List[Dict[str, Any]]
    similar_past_incidents: List[Dict[str, Any]]
    
    # Diagnostics & Reasoning
    diagnostic_findings: Dict[str, Any]
    root_cause: str
    root_cause_confidence: float
    resolution_guidance: Optional[str]
    
    # Proposed Remediation & Risk Analysis
    proposed_action: str
    action_type: str # restart_service, flush_connection_pool, clear_cache
    target_service: str
    is_risky: bool
    risk_justification: str
    
    # Human-in-the-Loop Approval Gate
    human_approval_required: bool
    human_approval_status: str # PENDING, APPROVED, REJECTED
    human_feedback: Optional[str]
    execution_result: str
    
    # Verification & Reflection
    verification_status: str # PENDING, VERIFIED_HEALTHY, VERIFICATION_FAILED
    verification_details: str
    reflection_count: int
    max_reflections: int
    is_resolved: bool
    resolution_notes: str
    
    # Step Audit Trail for UI streaming
    current_node: str
    step_logs: List[Dict[str, Any]]
