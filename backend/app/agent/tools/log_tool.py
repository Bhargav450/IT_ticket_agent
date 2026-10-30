from typing import Dict, Any, List, Optional
from app.services.infra_simulator import infra_simulator

def query_application_logs(service_name: Optional[str] = None, level: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Queries recent application and system logs for error stack traces, trace IDs, and diagnostic clues."""
    logs = infra_simulator.get_logs(service=service_name, level=level, limit=limit)
    return {
        "status": "success",
        "service_queried": service_name or "all",
        "log_count": len(logs),
        "logs": logs
    }

