import os
import random
from typing import List, Optional
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.services.seed_data import seed_database
from app.agent.runner import run_agent_for_incident

from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.knowledge import router as knowledge_router
from app.api.infra import router as infra_router
from app.api.analytics import router as analytics_router

# Create DB tables
Base.metadata.create_all(bind=engine)

# Seed initial knowledge base & default data
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

# ── Startup diagnostics ────────────────────────────────────────────────────────
print(f"[STARTUP] ZAMMAD_URL   : {settings.ZAMMAD_URL}", flush=True)
print(f"[STARTUP] ZAMMAD_TOKEN : {'SET ✅' if settings.ZAMMAD_TOKEN else 'NOT SET ❌'}", flush=True)
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous IT Support Agent Orchestrated with LangGraph"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root status endpoints
@app.get("/")
@app.get("/api")
@app.get("/api/")
def root():
    return {
        "message": "AegisOps Autonomous IT Support Agent API is running!",
        "status": "healthy",
        "interactive_docs": "/docs",
        "endpoints": {
            "incidents": "/api/incidents",
            "infra_services": "/api/infra/services",
            "knowledge_base": "/api/knowledge",
            "analytics": "/api/analytics/summary",
            "health": "/health"
        }
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ollama_model": settings.OLLAMA_MODEL,
        "ollama_endpoint": settings.OLLAMA_BASE_URL
    }

@app.get("/api/incidents", response_model=List[IncidentResponse])
@app.get("/api/incidents/", response_model=List[IncidentResponse])
@app.get("/incidents", response_model=List[IncidentResponse])
@app.get("/incidents/", response_model=List[IncidentResponse])
def get_incidents_direct(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(Incident.created_at.desc()).all()

# NOTE: POST /api/incidents is intentionally handled ONLY by incidents_router
# (backend/app/api/incidents.py → create_incident) which calls create_zammad_ticket.
# Do NOT add a duplicate POST handler here — it would bypass Zammad integration.

# Register all Routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(infra_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

# Also register directly for non-prefix calls
app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(knowledge_router)
app.include_router(infra_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
