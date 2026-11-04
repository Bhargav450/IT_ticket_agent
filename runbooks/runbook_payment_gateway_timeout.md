# Runbook: Payment Gateway 504 Timeout & Worker Deadlock
**Service**: `payment-gateway`  
**Category**: `APPLICATION`  
**Default Severity**: `P1_CRITICAL`  

## 1. Overview
The `payment-gateway` microservice processes asynchronous transactions, credit card authorizations, and webhook callbacks with external providers (Stripe, Adyen).

## 2. Symptoms
- HTTP 504 Gateway Timeout during checkout payment authorization.
- Webhook acknowledgment backlog exceeding 500 unprocessed events.
- Client checkout requests failing with payment processing timeout after 30 seconds.
- Socket deadlock in payment processing worker pool.

## 3. Diagnostic Checklist
1. Query `payment-gateway` logs for timeout traces (`Upstream payment provider timeout after 30000ms`).
2. Check CPU saturation and worker thread state (`deadlock detected in worker-thread-02`).
3. Verify external webhook endpoint connectivity.

## 4. Remediation Procedure
- **Action**: Execute graceful service restart via `execute_service_restart(service_name='payment-gateway')`.
- **Risk Level**: **HIGH**. Restarting the payment gateway may interrupt in-flight authorization handshakes.
- **Human Approval**: **MANDATORY**. SRE or On-call Lead sign-off is required before recycling workers.

## 5. Verification
- Probe `/health` endpoint and verify HTTP 200 OK.
- Verify error rate drops to 0.0% and average latency returns below 100ms.
- Send synthetic ping transaction to verify checkout route.

