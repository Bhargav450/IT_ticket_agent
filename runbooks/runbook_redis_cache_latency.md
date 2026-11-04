# Runbook: Redis Cache Memory Surge & Latency Spikes
**Service**: `redis-cache`  
**Category**: `INFRASTRUCTURE` / `CACHE`  
**Default Severity**: `P3_MEDIUM`  

## 1. Overview
The in-memory Redis caching layer sits between the `api-gateway` and persistent storage (`order-db`). It handles session tokens, product catalog caching, and rate limiting counters.

## 2. Symptoms
- Cache latency spikes from <2ms to >80ms.
- Cache hit ratio drops below 50%.
- Out-of-memory (OOM) evictions reported in Redis system logs.
- Memory usage exceeds 90% threshold.

## 3. Diagnostic Checklist
1. Query system logs for `OOM command not allowed` or `evicted_keys` surge.
2. Check memory utilization percentage and active connections.
3. Validate keyspace expiration policies.

## 4. Remediation Procedure
- **Action**: Execute cache key purge / flush stale namespaces via `clear_cache(service_name='redis-cache')`.
- **Risk Level**: **LOW**. Flushing Redis cache will temporarily cause upstream services to hit database directly, but will not cause data corruption or drop connections.
- **Human Approval**: Not required for automated remediation.

## 5. Verification
- Verify Redis memory drops below 50%.
- Probe Redis latency returns to <5ms.
- Verify `/healthz` or `PING` returns `PONG` (200 OK).

