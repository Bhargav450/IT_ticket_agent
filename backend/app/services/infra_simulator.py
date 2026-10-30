from datetime import datetime
from typing import Dict, Any, List
import random

class InfraSimulator:
    def __init__(self):
        self.reset_to_healthy()

    def reset_to_healthy(self):
        self.services: Dict[str, Dict[str, Any]] = {
            "api-gateway": {
                "service_name": "api-gateway",
                "status": "HEALTHY",
                "latency_ms": 28.5,
                "error_rate_percent": 0.02,
                "cpu_percent": 34.0,
                "memory_percent": 41.5,
                "active_connections": 140,
                "version": "v2.14.0",
                "last_restarted": datetime.utcnow().isoformat(),
                "endpoints": {"/healthz": 200, "/api/v1/checkout": 200, "/api/v1/users": 200}
            },
            "order-db": {
                "service_name": "order-db",
                "status": "HEALTHY",
                "latency_ms": 4.2,
                "error_rate_percent": 0.0,
                "cpu_percent": 25.0,
                "memory_percent": 55.0,
                "active_connections": 18,
                "max_connections": 100,
                "idle_in_transaction": 0,
                "slow_queries_count": 0,
                "last_restarted": datetime.utcnow().isoformat(),
                "endpoints": {"ping": 200}
            },
            "auth-service": {
                "service_name": "auth-service",
                "status": "HEALTHY",
                "latency_ms": 15.1,
                "error_rate_percent": 0.01,
                "cpu_percent": 20.0,
                "memory_percent": 38.0,
                "active_connections": 45,
                "jwt_validation_failure_rate": 0.0,
                "last_restarted": datetime.utcnow().isoformat(),
                "endpoints": {"/auth/health": 200, "/auth/verify": 200}
            },
            "payment-gateway": {
                "service_name": "payment-gateway",
                "status": "HEALTHY",
                "latency_ms": 65.0,
                "error_rate_percent": 0.0,
                "cpu_percent": 18.0,
                "memory_percent": 30.0,
                "active_connections": 22,
                "last_restarted": datetime.utcnow().isoformat(),
                "endpoints": {"/health": 200}
            },
            "redis-cache": {
                "service_name": "redis-cache",
                "status": "HEALTHY",
                "latency_ms": 1.2,
                "error_rate_percent": 0.0,
                "cpu_percent": 12.0,
                "memory_percent": 48.0,
                "active_connections": 50,
                "last_restarted": datetime.utcnow().isoformat(),
                "endpoints": {"PING": 200}
            }
        }
        self.logs: List[Dict[str, Any]] = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "api-gateway",
                "level": "INFO",
                "message": "Gateway routing engine initialized. Upstreams: order-db, auth-service, payment-gateway healthy."
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "order-db",
                "level": "INFO",
                "message": "Connection pool initialized: min_size=10, max_size=100. Superuser connection reserved."
            }
        ]

    def trigger_failure(self, scenario: str) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        if scenario == "http_500_gateway":
            self.services["api-gateway"]["status"] = "CRITICAL"
            self.services["api-gateway"]["error_rate_percent"] = 48.7
            self.services["api-gateway"]["latency_ms"] = 3850.0
            self.services["api-gateway"]["cpu_percent"] = 92.4
            self.services["api-gateway"]["endpoints"]["/healthz"] = 500
            self.services["api-gateway"]["endpoints"]["/api/v1/checkout"] = 500
            
            self.logs.extend([
                {
                    "timestamp": timestamp,
                    "service": "api-gateway",
                    "level": "ERROR",
                    "trace_id": f"trace-{random.randint(10000, 99999)}",
                    "message": "HTTP 500 Internal Server Error: Worker process deadlock. Node worker pool exhausted, unable to dispatch incoming requests.",
                    "stack_trace": "Traceback (most recent call last):\n  File '/usr/src/app/gateway/proxy.py', line 142, in dispatch_request\n  TimeoutError: Upstream socket timeout after 5000ms. Worker worker-04 saturated."
                },
                {
                    "timestamp": timestamp,
                    "service": "api-gateway",
                    "level": "CRITICAL",
                    "trace_id": f"trace-{random.randint(10000, 99999)}",
                    "message": "Incoming traffic queue overflow. HTTP 500 returned to 48.7% of clients. Root cause points to unhandled promise leak in worker threads.",
                    "stack_trace": "SystemError: Worker memory limit exceeded (92.4% CPU, leaked sockets=412)."
                }
            ])
            return {"status": "triggered", "scenario": scenario, "service": "api-gateway"}

        elif scenario == "db_pool_exhaustion":
            self.services["order-db"]["status"] = "CRITICAL"
            self.services["order-db"]["active_connections"] = 100
            self.services["order-db"]["idle_in_transaction"] = 42
            self.services["order-db"]["slow_queries_count"] = 18
            self.services["order-db"]["latency_ms"] = 4820.0
            self.services["order-db"]["endpoints"]["ping"] = 504
            
            self.logs.extend([
                {
                    "timestamp": timestamp,
                    "service": "order-db",
                    "level": "ERROR",
                    "message": "OperationalError: remaining connection slots are reserved for non-replication superuser connections (max_connections=100 reached).",
                    "stack_trace": "psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections"
                },
                {
                    "timestamp": timestamp,
                    "service": "order-db",
                    "level": "CRITICAL",
                    "message": "QueuePool limit of size 50 overflow 20 reached, giving up. 42 connections stuck in 'IDLE in transaction' > 180s.",
                    "stack_trace": "sqlalchemy.exc.TimeoutError: QueuePool limit reached. Transactions blocking on exclusive row lock in table 'orders'."
                }
            ])
            return {"status": "triggered", "scenario": scenario, "service": "order-db"}

        elif scenario == "auth_token_failure":
            self.services["auth-service"]["status"] = "DEGRADED"
            self.services["auth-service"]["error_rate_percent"] = 35.2
            self.services["auth-service"]["jwt_validation_failure_rate"] = 0.82
            self.services["auth-service"]["endpoints"]["/auth/verify"] = 401
            
            self.logs.append({
                "timestamp": timestamp,
                "service": "auth-service",
                "level": "ERROR",
                "message": "JWT Signature Verification Failed: Key ID 'kid-2024-q3' expired. Identity provider JWKS public key cache out of sync.",
                "stack_trace": "jose.exceptions.JWTError: Signature verification failed. JWKS certificate rotation missing in local in-memory cache."
            })
            return {"status": "triggered", "scenario": scenario, "service": "auth-service"}
        
        return {"status": "unknown scenario"}

    def get_logs(self, service: str = None, level: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        filtered = self.logs
        if service:
            filtered = [l for l in filtered if l.get("service") == service]
        if level:
            filtered = [l for l in filtered if l.get("level") == level]
        return filtered[-limit:]

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        return self.services.get(service_name, {"status": "UNKNOWN"})

    def get_all_services(self) -> List[Dict[str, Any]]:
        return list(self.services.values())

    def restart_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.services:
            return {"success": False, "message": f"Service '{service_name}' not found."}
        
        # Service recovery
        s = self.services[service_name]
        s["status"] = "HEALTHY"
        s["error_rate_percent"] = 0.01
        s["latency_ms"] = 32.0
        s["cpu_percent"] = 28.0
        s["last_restarted"] = datetime.utcnow().isoformat()
        
        # Reset endpoints
        for ep in s.get("endpoints", {}):
            s["endpoints"][ep] = 200

        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": service_name,
            "level": "INFO",
            "message": f"Service '{service_name}' successfully restarted by Autonomous IT Support Agent. Worker pool regenerated, sockets cleared."
        })
        return {"success": True, "service": service_name, "status": "HEALTHY", "action": "restarted"}

    def flush_connection_pool(self, database_name: str) -> Dict[str, Any]:
        if database_name not in self.services:
            return {"success": False, "message": f"Database '{database_name}' not found."}
        
        db = self.services[database_name]
        db["status"] = "HEALTHY"
        db["active_connections"] = 12
        db["idle_in_transaction"] = 0
        db["slow_queries_count"] = 0
        db["latency_ms"] = 3.8
        db["endpoints"]["ping"] = 200

        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": database_name,
            "level": "INFO",
            "message": f"Connection pool on '{database_name}' flushed. Terminated 42 idle transactions. Active connections reset to 12/100."
        })
        return {"success": True, "database": database_name, "active_connections": 12, "status": "HEALTHY"}

    def clear_cache(self, service_name: str) -> Dict[str, Any]:
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": service_name,
            "level": "INFO",
            "message": f"Cache purged on '{service_name}'. Cache keys invalidated."
        })
        return {"success": True, "service": service_name, "action": "cache_cleared"}

    def probe_health(self, service_name: str, endpoint: str = "/healthz") -> Dict[str, Any]:
        s = self.services.get(service_name)
        if not s:
            return {"healthy": False, "status_code": 404, "message": "Service not found"}
        
        code = s.get("endpoints", {}).get(endpoint, 200 if s["status"] == "HEALTHY" else 500)
        return {
            "healthy": (code == 200),
            "status_code": code,
            "latency_ms": s.get("latency_ms", 25.0),
            "error_rate_percent": s.get("error_rate_percent", 0.0),
            "service_status": s.get("status")
        }

infra_simulator = InfraSimulator()

