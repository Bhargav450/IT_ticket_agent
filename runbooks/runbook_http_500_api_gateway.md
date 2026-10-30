# SOP-201: Troubleshooting HTTP 500 Internal Server Error in API Gateway

## Incident Overview
- **Service Affected**: `api-gateway`, `checkout-service`, `catalog-service`
- **Severity**: P1 / P2
- **Common Symptoms**: Users report "500 Internal Server Error", "Cannot access application", "Service Unavailable 503".

## Root Cause Analysis (RCA) Vectors
1. **Upstream Microservice Failure**: The gateway cannot establish a handshake or receives an uncaught exception from downstream services (e.g. `auth-service` or `payment-gateway`).
2. **Connection Timeout**: Gateway proxy timeout triggered because downstream query latency > 5000ms.
3. **Out of Memory (OOM) or Worker Saturation**: Node/Uvicorn workers maxed out due to leaked sockets or unhandled promise rejections.

## Diagnostic Procedures
1. Run `query_application_logs` with filter `level="ERROR"` and `service="api-gateway"`.
2. Inspect stack traces for `ConnectionRefusedError`, `502 Bad Gateway`, or `PoolTimeout`.
3. Check `get_service_status` for `api-gateway` and downstream dependencies (`auth-service`, `payment-gateway`).
4. If logs show `Database connection timeout`, escalate check to `db-diagnostic-tool`.

## Remediation & Recovery Actions
### Safe Actions (Autonomous Execution Permitted)
- **Clear Redis Gateway Cache**: `clear_gateway_cache` (Risk: Low. Flushes cached routing tables).
- **Scale Pod Replicas**: If CPU > 85%, scale up gateway pods by 2 instances (Risk: Low).

### Risky Actions (HUMAN APPROVAL REQUIRED)
- **Restart Core API Gateway Service**: `restart_service(service="api-gateway")` (Risk: High. Causes 5-10s packet drop).
- **Rollback Configuration Deployment**: `rollback_deployment(service="api-gateway", version="previous")` (Risk: High. Reverts runtime config).

## Verification Step
1. Execute `probe_service_health(service="api-gateway", endpoint="/healthz")`. Expected HTTP Status: `200 OK`.
2. Confirm error rate drops below 0.1% within 60 seconds.
3. If still returning 500, check `auth-service` dependency.
