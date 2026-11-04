import uuid
from app.core.database import SessionLocal, Base, engine
from app.models.incident import Incident
from app.services.seed_data import seed_database
from app.services.infra_simulator import infra_simulator
from app.agent.runner import run_agent_for_incident, resume_agent_with_approval

def test_database_incident_lifecycle():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)

    # 1. Trigger DB failure
    infra_simulator.trigger_failure("db_pool_exhaustion")
    assert infra_simulator.get_service_status("order-db")["status"] == "CRITICAL"

    # 2. Raise Ticket
    incident = Incident(
        ticket_number=f"TEST-DB-{uuid.uuid4().hex[:6]}",
        title="Database connection timeout during checkout surge",
        description="Database queries failing with OperationalError: remaining connection slots are reserved for non-replication superuser connections. QueuePool limit reached.",
        reporter_email="devops@enterprise.io",
        status="OPEN"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # 3. Agent Execution
    res = run_agent_for_incident(db, incident.id)
    db.expire_all()
    db.refresh(incident)

    assert incident.category == "DATABASE"
    assert incident.affected_service == "order-db"
    assert any(term in incident.root_cause_analysis.lower() for term in ["connection slots", "connection pool", "queuepool", "connections"])
    assert incident.action_risk_level == "HIGH"
    assert incident.status == "AWAITING_APPROVAL"

    # 4. Human Approval
    resume_agent_with_approval(db, incident.id, approved=True, feedback="Approved to flush DB pool.")
    db.expire_all()
    db.refresh(incident)

    assert incident.status == "RESOLVED"
    assert incident.verification_status == "VERIFIED_HEALTHY"
    assert infra_simulator.get_service_status("order-db")["status"] == "HEALTHY"
    print("\n[SUCCESS] Database connection pool incident autonomously resolved!")
    db.close()

if __name__ == "__main__":
    test_database_incident_lifecycle()

