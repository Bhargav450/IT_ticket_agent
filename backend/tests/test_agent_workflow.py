import uuid
from app.core.database import SessionLocal, Base, engine
from app.models.incident import Incident
from app.services.seed_data import seed_database
from app.services.infra_simulator import infra_simulator
from app.agent.runner import run_agent_for_incident, resume_agent_with_approval

def test_full_autonomous_support_lifecycle():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)

    # 1. Trigger simulated infrastructure failure: HTTP 500 in api-gateway
    failure_res = infra_simulator.trigger_failure("http_500_gateway")
    assert failure_res["service"] == "api-gateway"
    assert infra_simulator.get_service_status("api-gateway")["status"] == "CRITICAL"

    # 2. Employee reports incident with unique ticket number
    unique_ticket = f"TEST-INC-{uuid.uuid4().hex[:6]}"
    incident = Incident(
        ticket_number=unique_ticket,
        title="Application returning HTTP 500 errors. Cannot access checkout.",
        description="My application is returning HTTP 500 errors. I cannot access the application.",
        reporter_email="employee@enterprise.io",
        status="OPEN"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # 3. Trigger LangGraph Autonomous Agent
    res = run_agent_for_incident(db, incident.id)
    db.expire_all()
    db.refresh(incident)

    # Verify Triage, RAG, and Diagnostic occurred
    assert incident.category == "APPLICATION"
    assert incident.affected_service == "api-gateway"
    assert incident.root_cause_analysis is not None
    assert len(incident.rag_sources) > 0
    print(f"\n[TEST] Diagnosed Root Cause: {incident.root_cause_analysis}")
    print(f"[TEST] Proposed Action: {incident.proposed_action}")
    print(f"[TEST] Action Risk Level: {incident.action_risk_level}")

    # Verify Human-in-the-Loop was triggered for risky action (restart)
    assert incident.human_approval_required is True
    assert incident.status == "AWAITING_APPROVAL"
    assert incident.human_approval_status == "PENDING"
    print("[TEST] Passed Human-in-the-Loop Interruption Gate successfully!")

    # 4. Human Support Engineer approves the action
    approval_res = resume_agent_with_approval(
        db=db,
        incident_id=incident.id,
        approved=True,
        feedback="Approved by SRE On-call engineer Sarah Chen."
    )
    db.expire_all()
    db.refresh(incident)

    # Verify action executed & verification node confirmed resolution
    print(f"[TEST] Post-Approval Status: {incident.status}")
    print(f"[TEST] Verification Status: {incident.verification_status}")
    print(f"[TEST] Resolution Notes: {incident.resolution_notes}")
    
    assert incident.status == "RESOLVED"
    assert incident.verification_status == "VERIFIED_HEALTHY"
    assert infra_simulator.get_service_status("api-gateway")["status"] == "HEALTHY"
    
    print("\n[SUCCESS] Entire Autonomous IT Support Agent lifecycle tested and passed!")
    db.close()

if __name__ == "__main__":
    test_full_autonomous_support_lifecycle()
