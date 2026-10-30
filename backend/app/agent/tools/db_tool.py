from typing import Dict, Any
from app.services.infra_simulator import infra_simulator

def query_db_diagnostics(database_name: str = "order-db") -> Dict[str, Any]:
    """Inspects database connection pool, active connections, lock waits, slow queries, and latency."""
    service = infra_simulator.get_service_status(database_name)
    if service.get("status") == "UNKNOWN":
        return {"status": "error", "message": f"Database {database_name} not found"}
    
    return {
        "status": "success",
        "database": database_name,
        "health": service.get("status"),
        "active_connections": service.get("active_connections", 0),
        "max_connections": service.get("max_connections", 100),
        "idle_in_transaction_count": service.get("idle_in_transaction", 0),
        "slow_queries_count": service.get("slow_queries_count", 0),
        "query_latency_ms": service.get("latency_ms", 0.0),
        "is_saturated": service.get("active_connections", 0) >= service.get("max_connections", 100) * 0.8
    }

