# SOP-304: Database Connection Pool Exhaustion & Query Latency

## Incident Overview
- **Service Affected**: `order-db`, `postgres-cluster`, `inventory-service`
- **Severity**: P1 / P2
- **Common Symptoms**: Application throws `OperationalError: remaining connection slots are reserved for non-replication superuser connections` or `TimeoutError: QueuePool limit of size 20 overflow 10 reached, giving up`.

## Root Cause Analysis
1. **Connection Leak**: Unclosed session contexts in worker threads holding connections idle in transaction (`IDLE in transaction > 120s`).
2. **Slow / Long-running Analytical Queries**: Heavy report query blocking table rows with exclusive locks.
3. **Traffic Surge**: Sudden spike in incoming checkout requests exceeding configured pool max (`pool_size=50`, `max_overflow=20`).

## Diagnostic Procedures
1. Run `query_db_diagnostics` for `database="order-db"`.
2. Inspect `active_connections`, `idle_in_transaction_count`, and `slow_queries_count`.
3. Check `lock_waits` table to see if transactions are blocked waiting on row locks.

## Remediation & Recovery Actions
### Safe Actions (Autonomous Execution Permitted)
- **Terminate Long Idle Connections**: `terminate_idle_connections(max_idle_seconds=180)` (Risk: Low).
- **Enable Read-Only Replica Traffic Shift**: Route read queries to replica (Risk: Low).

### Risky Actions (HUMAN APPROVAL REQUIRED)
- **Flush Database Connection Pool**: `flush_connection_pool(database="order-db")` (Risk: High. Terminates existing active worker pools).
- **Restart Database Service Instance**: `restart_service(service="postgres-cluster")` (Risk: Critical. Requires maintenance downtime).

## Verification Step
1. Check `query_db_diagnostics` again; verify `active_connections` < 70% threshold.
2. Verify latency on synthetic ping query `SELECT 1` is < 5ms.
3. Ensure no new `PoolTimeout` errors in application logs.
