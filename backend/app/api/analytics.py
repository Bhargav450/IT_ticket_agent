from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.incident import Incident
from app.models.audit import AgentStepLog

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_incidents = db.query(Incident).count()
    resolved_incidents = db.query(Incident).filter(Incident.status == "RESOLVED").count()
    awaiting_approval = db.query(Incident).filter(Incident.status == "AWAITING_APPROVAL").count()
    investigating = db.query(Incident).filter(Incident.status.in_(["OPEN", "INVESTIGATING", "VERIFYING"])).count()
    
    # Calculate MTTR
    durations = [i.resolution_time_seconds for i in db.query(Incident).filter(Incident.status == "RESOLVED").all() if i.resolution_time_seconds]
    avg_mttr = round(sum(durations) / len(durations), 1) if durations else 42.0

    # Human-in-the-loop vs Autonomous
    human_approved = db.query(Incident).filter(Incident.human_approval_status == "APPROVED").count()
    autonomous = max(0, resolved_incidents - human_approved)

    # Tool invocation counts
    tool_counts = (
        db.query(AgentStepLog.tool_name, func.count(AgentStepLog.id))
        .filter(AgentStepLog.tool_name.isnot(None))
        .group_by(AgentStepLog.tool_name)
        .all()
    )

    # Category counts
    cat_counts = (
        db.query(Incident.category, func.count(Incident.id))
        .group_by(Incident.category)
        .all()
    )

    return {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "awaiting_approval": awaiting_approval,
        "active_investigating": investigating,
        "mttr_seconds": avg_mttr,
        "autonomy_rate_percent": round((autonomous / max(1, resolved_incidents)) * 100, 1),
        "tool_usage": {name or "unspecified": count for name, count in tool_counts},
        "category_distribution": {cat or "OTHER": count for cat, count in cat_counts}
    }

