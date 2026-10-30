from typing import Dict, Any
from app.agent.state import ITSupportState
from app.agent.tools.infra_tool import probe_service_health
from app.agent.tools.ticket_tool import update_incident_record
from app.agent.memory.incident_memory import incident_memory
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def verification_node(state: ITSupportState) -> Dict[str, Any]:
    """Verification Agent: Verifies system recovery via synthetic health probes, reflects on outcomes, and finalizes resolution."""
    service = state.get("affected_service", "api-gateway")
    action_executed = state.get("action_executed", False)
    reflection_count = state.get("reflection_count", 0)
    max_reflections = state.get("max_reflections", 2)
    
    if not action_executed:
        return {
            "verified": True,
            "is_resolved": False,
            "verification_status": "SKIPPED",
            "current_node": "verification"
        }

    endpoint = "/healthz"
    if service == "order-db":
        endpoint = "ping"
    elif service == "auth-service":
        endpoint = "/auth/health"
    elif service == "redis-cache":
        endpoint = "PING"

    probe = probe_service_health(service, endpoint)
    is_healthy = probe.get("healthy", False)
    status_code = probe.get("status_code", 500)
    latency_ms = probe.get("latency_ms", 0)

    db = SessionLocal()
    try:
        if is_healthy:
            thought = f"Verification probe to '{service}{endpoint}' succeeded with HTTP {status_code} (latency: {latency_ms:.1f}ms). Service metrics returned to normal baseline."
            summary = (
                f"Incident autonomously diagnosed and resolved. "
                f"Root cause: {state.get('root_cause')}. "
                f"Remediation action: {state.get('proposed_action')}. "
                f"Post-recovery probe confirmed service '{service}' healthy at {status_code} OK."
            )

            step = AgentStepLog(
                incident_id=state["incident_id"],
                node_name="verification",
                status="SUCCESS",
                thought_summary=thought,
                tool_name="probe_service_health",
                tool_input={"service": service, "endpoint": endpoint},
                tool_output={"healthy": True, "status_code": status_code, "latency_ms": latency_ms}
            )
            db.add(step)

            update_incident_record(
                db=db,
                incident_id=state["incident_id"],
                status="RESOLVED",
                verification_status="VERIFIED_HEALTHY",
                verification_details=f"Synthetic probe passed. Status: {status_code} OK, Latency: {latency_ms:.1f}ms",
                resolution_notes=summary,
                reflection_count=reflection_count
            )
            db.commit()

            return {
                "verified": True,
                "is_resolved": True,
                "verification_status": "VERIFIED_HEALTHY",
                "verification_details": thought,
                "resolution_notes": summary,
                "current_node": "verification_completed"
            }
        else:
            reflection_count += 1
            thought = f"Verification probe failed! Service '{service}' returned HTTP {status_code}. Reflection attempt {reflection_count}/{max_reflections}."
            
            step = AgentStepLog(
                incident_id=state["incident_id"],
                node_name="verification_reflection",
                status="VERIFICATION_FAILED",
                thought_summary=thought,
                tool_name="probe_service_health",
                tool_input={"service": service, "endpoint": endpoint},
                tool_output={"healthy": False, "status_code": status_code}
            )
            db.add(step)

            if reflection_count >= max_reflections:
                escalation_note = f"Automated remediation failed after {reflection_count} verification attempts. Escalating incident to Senior On-Call Engineer."
                update_incident_record(
                    db=db,
                    incident_id=state["incident_id"],
                    status="ESCALATED",
                    verification_status="VERIFICATION_FAILED",
                    resolution_notes=escalation_note,
                    reflection_count=reflection_count
                )
                db.commit()
                return {
                    "verified": True,
                    "is_resolved": False,
                    "verification_status": "ESCALATED",
                    "verification_details": escalation_note,
                    "reflection_count": reflection_count,
                    "current_node": "verification_escalated"
                }

            update_incident_record(
                db=db,
                incident_id=state["incident_id"],
                status="INVESTIGATING",
                reflection_count=reflection_count
            )
            db.commit()

            return {
                "verified": False,
                "diagnosed": False, # Trigger re-diagnosis
                "is_resolved": False,
                "verification_status": "FAILED_RETRYING",
                "verification_details": thought,
                "reflection_count": reflection_count,
                "current_node": "verification_loopback"
            }
    finally:
        db.close()
