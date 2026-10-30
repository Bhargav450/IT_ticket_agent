import os
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.incident import Incident
from app.models.knowledge import KnowledgeDocument
from app.core.security import get_password_hash
from app.services.rag_engine import rag_engine

def seed_database(db: Session):
    # 1. Seed Default Support Engineer User
    user = db.query(User).filter(User.email == "engineer@enterprise.io").first()
    if not user:
        user = User(
            email="engineer@enterprise.io",
            full_name="Sarah Chen (Lead Site Reliability Engineer)",
            hashed_password=get_password_hash("password123"),
            role="support_engineer",
            is_active=True
        )
        db.add(user)
        db.commit()

    # 2. Seed Runbooks into RAG Knowledge Base
    runbook_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../runbooks"))
    if os.path.exists(runbook_dir):
        for fname in os.listdir(runbook_dir):
            if fname.endswith(".md"):
                fpath = os.path.join(runbook_dir, fname)
                title = fname.replace(".md", "").replace("_", " ").title()
                
                existing = db.query(KnowledgeDocument).filter(KnowledgeDocument.filename == fname).first()
                if not existing:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    rag_engine.ingest_document(
                        db=db,
                        filename=fname,
                        title=title,
                        category="RUNBOOK",
                        content=content
                    )

    # 3. Seed Sample Initial Incidents
    sample_incidents = [
        {
            "ticket_number": "INC-2026-101",
            "title": "Application returning HTTP 500 errors - users unable to checkout",
            "description": "My application is returning HTTP 500 errors. I cannot access the application and users report checkout page is down.",
            "status": "OPEN",
            "severity": "P1_CRITICAL",
            "category": "APPLICATION",
            "affected_service": "api-gateway",
            "reporter_email": "alex.sales@enterprise.io"
        },
        {
            "ticket_number": "INC-2026-102",
            "title": "Order database connection timeout during high load",
            "description": "Database queries failing with OperationalError: remaining connection slots are reserved. Checkout microservice timing out.",
            "status": "OPEN",
            "severity": "P2_HIGH",
            "category": "DATABASE",
            "affected_service": "order-db",
            "reporter_email": "devops-oncall@enterprise.io"
        },
        {
            "ticket_number": "INC-2026-103",
            "title": "Users being logged out randomly with 401 Unauthorized",
            "description": "Multiple employees reported getting kicked out of internal dashboards with JWT signature verification errors.",
            "status": "RESOLVED",
            "severity": "P3_MEDIUM",
            "category": "AUTHENTICATION",
            "affected_service": "auth-service",
            "reporter_email": "hr-ops@enterprise.io",
            "root_cause_analysis": "JWKS key rotation occurred on auth provider without cache invalidation.",
            "resolution_notes": "Autonomous agent refreshed JWKS cache and validated token endpoints.",
            "resolution_time_seconds": 45
        }
    ]

    for inc in sample_incidents:
        existing = db.query(Incident).filter(Incident.ticket_number == inc["ticket_number"]).first()
        if not existing:
            new_inc = Incident(**inc)
            db.add(new_inc)
    
    db.commit()
