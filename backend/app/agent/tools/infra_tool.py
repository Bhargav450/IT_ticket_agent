from typing import Dict, Any
from app.services.infra_simulator import infra_simulator

def get_service_status(service_name: str) -> Dict[str, Any]:
    """Retrieves current metrics, latency, error rate, and CPU/memory utilization of a service."""
    return infra_simulator.get_service_status(service_name)

def probe_service_health(service_name: str, endpoint: str = "/healthz") -> Dict[str, Any]:
    """Probes an HTTP health endpoint to verify if the service is responding with 200 OK."""
    return infra_simulator.probe_health(service_name, endpoint)

def clear_cache(service_name: str = "api-gateway") -> Dict[str, Any]:
    """Safe action: clears temporary routing and response cache."""
    return infra_simulator.clear_cache(service_name)

def execute_service_restart(service_name: str) -> Dict[str, Any]:
    """Risky action: Restarts the microservice process and recycles worker threads."""
    return infra_simulator.restart_service(service_name)

def execute_flush_db_pool(database_name: str) -> Dict[str, Any]:
    """Risky action: Flushes all active and idle database connection pool slots."""
    return infra_simulator.flush_connection_pool(database_name)
