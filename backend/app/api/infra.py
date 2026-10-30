from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from app.services.infra_simulator import infra_simulator
from app.schemas.agent import ServiceStatusSchema, SimulatedFailureRequest

router = APIRouter(prefix="/infra", tags=["infrastructure"])

@router.get("/services", response_model=List[ServiceStatusSchema])
def get_services():
    return infra_simulator.get_all_services()

@router.get("/logs")
def get_logs(service: Optional[str] = None, level: Optional[str] = None, limit: int = 30):
    return infra_simulator.get_logs(service=service, level=level, limit=limit)

@router.post("/simulate-failure")
def simulate_failure(req: SimulatedFailureRequest):
    return infra_simulator.trigger_failure(req.scenario)

@router.post("/reset")
def reset_infra():
    infra_simulator.reset_to_healthy()
    return {"status": "success", "message": "All infrastructure services restored to baseline HEALTHY."}
