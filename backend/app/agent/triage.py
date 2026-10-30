from typing import Dict, Any
from app.agent.state import ITSupportState
from app.agent.llm_factory import llm_client
from app.agent.tools.ticket_tool import update_incident_record
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def triage_node(state: ITSupportState) -> Dict[str, Any]:
    """Triage Agent: Evaluates ticket title and description, extracts affected service, and assigns severity."""
    title = state.get("title", "")
    desc = state.get("description", "")
    
    prompt = f"""
    You are an expert IT Incident Triage Agent.
    Analyze this incident report:
    Title: {title}
    Description: {desc}

    Return JSON with:
    - category: (APPLICATION | DATABASE | AUTHENTICATION | INFRASTRUCTURE)
    - severity: (P1_CRITICAL | P2_HIGH | P3_MEDIUM | P4_LOW)
    - affected_service: (api-gateway | order-db | auth-service | payment-gateway | redis-cache)
    - reasoning: brief explanation
    """
    
    system = "You are a specialized Triage Agent in an enterprise IT support center. Classify accurately."
    result = llm_client.generate_json(prompt, system)
    
    category = result.get("category", "APPLICATION")
    severity = result.get("severity", "P2_HIGH")
    service = result.get("affected_service", "api-gateway")
    reasoning = result.get("reasoning", "Classified based on ticket symptoms and keywords.")
    
    # Fallback sanity checks
    text = f"{title} {desc}".lower()
    if "500" in text or "crash" in text or "outage" in text or "cannot access" in text:
        severity = "P1_CRITICAL"
        category = "APPLICATION"
        service = "api-gateway"
    elif "pool" in text or "database" in text or "sql" in text:
        severity = "P2_HIGH"
        category = "DATABASE"
        service = "order-db"
    elif "401" in text or "token" in text or "auth" in text:
        severity = "P2_HIGH"
        category = "AUTHENTICATION"
        service = "auth-service"

    # Persist audit step
    db = SessionLocal()
    try:
        step = AgentStepLog(
            incident_id=state["incident_id"],
            node_name="triage",
            status="SUCCESS",
            thought_summary=f"Incident classified as {severity} {category}. Identified primary impacted service as '{service}'. Reasoning: {reasoning}",
            tool_name="triage_classifier",
            tool_input={"title": title, "description": desc},
            tool_output={"category": category, "severity": severity, "affected_service": service}
        )
        db.add(step)
        
        # Update incident record with classification
        update_incident_record(
            db=db,
            incident_id=state["incident_id"],
            status="INVESTIGATING",
            category=category,
            severity=severity,
            affected_service=service
        )
        db.commit()
    finally:
        db.close()

    return {
        "triaged": True,
        "category": category,
        "severity": severity,
        "affected_service": service,
        "triage_reasoning": reasoning,
        "current_node": "triage"
    }
