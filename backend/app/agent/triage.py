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
    You are an expert IT Incident Triage Agent in an enterprise Site Reliability Engineering center.
    Analyze this incident report:
    Title: {title}
    Description: {desc}

    Enterprise ITIL Severity Standards:
    - P1_CRITICAL: Complete internal infrastructure outage, revenue blocker, checkout failure, customer-facing down (e.g. HTTP 500 error cascade on api-gateway, HTTP 504 checkout failure on payment-gateway).
    - P2_HIGH: Core system degraded, database connection pool exhaustion, authentication or token failure across users.
    - P3_MEDIUM: Performance degradation, elevated latency, high memory usage, cache eviction, partial performance issue.
    - P4_LOW: Standard IT requests, how-to inquiries, access requests, VPN setup, blocked external websites or content filter policy inquiries (e.g. YouTube, media streaming), documentation requests.

    Enterprise Technical Categories:
    - APPLICATION: Internal company services and APIs (checkout, order processing, internal web portals).
    - DATABASE: PostgreSQL, connection pools, SQL deadlocks, queries.
    - AUTHENTICATION: JWT tokens, JWKS keys, login, session validation, SSO.
    - INFRASTRUCTURE: Caching tiers (Redis), CPU/memory saturation, container nodes.
    - GENERAL_IT: Employee workspace, laptop issues, VPN, corporate web filtering, blocked websites/URLs (YouTube, video/media streaming), access requests, IT policy inquiries.

    Service Mapping Rules:
    - api-gateway: HTTP 500 Internal Server Error, internal backend application down, routing failure.
    - order-db: Database connection timeouts, SQL errors, connection pool exhaustion.
    - auth-service: JWT verification, authentication tokens, 401 Unauthorized.
    - payment-gateway: Credit card authorization failure, payment 504 timeout on Stripe.
    - redis-cache: Cache memory saturation, Redis OOM eviction.
    - enterprise-it: VPN setup, employee workspace, corporate web filtering, blocked websites or URLs (e.g. YouTube, streaming media), access requests.

    Return strictly valid JSON:
    {{
      "severity": "P1_CRITICAL" | "P2_HIGH" | "P3_MEDIUM" | "P4_LOW",
      "category": "APPLICATION" | "DATABASE" | "AUTHENTICATION" | "INFRASTRUCTURE" | "GENERAL_IT",
      "affected_service": "api-gateway" | "order-db" | "auth-service" | "payment-gateway" | "redis-cache" | "enterprise-it",
      "reasoning": "brief explanation"
    }}
    """
    
    system = "You are a specialized Triage Agent in an enterprise IT support center. Classify accurately using ITIL standards."
    result = llm_client.generate_json(prompt, system)
    
    sev_raw = str(result.get("severity", "P2_HIGH")).upper()
    if "P1" in sev_raw or "CRITICAL" in sev_raw:
        severity = "P1_CRITICAL"
    elif "P2" in sev_raw or "HIGH" in sev_raw:
        severity = "P2_HIGH"
    elif "P3" in sev_raw or "MEDIUM" in sev_raw:
        severity = "P3_MEDIUM"
    elif "P4" in sev_raw or "LOW" in sev_raw:
        severity = "P4_LOW"
    else:
        severity = "P2_HIGH"

    cat_raw = str(result.get("category", "APPLICATION")).upper()
    if "DATA" in cat_raw or "SQL" in cat_raw:
        category = "DATABASE"
    elif "AUTH" in cat_raw:
        category = "AUTHENTICATION"
    elif "INFRA" in cat_raw or "CACHE" in cat_raw:
        category = "INFRASTRUCTURE"
    elif "GENERAL" in cat_raw or "IT" in cat_raw or "POLICY" in cat_raw:
        category = "GENERAL_IT"
    else:
        category = "APPLICATION"

    service = str(result.get("affected_service", "enterprise-it")).lower().strip()
    reasoning = result.get("reasoning", "Classified dynamically by autonomous agent.")

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
