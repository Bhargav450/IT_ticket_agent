# SOP-102: Authentication Service Token Validation Failure (401 / 403 Cascades)

## Incident Overview
- **Service Affected**: `auth-service`, `user-session-store`
- **Severity**: P2
- **Common Symptoms**: Users logged out unexpectedly, API returns `401 Unauthorized: Signature verification failed`, or SSO identity provider handshake timeout.

## Root Cause Analysis
1. **Clock Skew or Expired Signing Key**: Secret key rotation occurred without rolling grace period.
2. **Redis Token Cache Down**: Session lookup failing with `ConnectionRefusedError: redis:6379`.
3. **LDAP/IdP Network Partition**: Firewall or proxy blocking external IdP JWKS endpoint.

## Diagnostic Procedures
1. Run `query_application_logs` for `service="auth-service"` with keyword `"token"`.
2. Inspect `get_service_status(service="redis-cache")` and `get_service_status(service="auth-service")`.
3. Validate JWKS cache status and signing certificate expiry timestamp.

## Remediation & Recovery Actions
### Safe Actions (Autonomous Execution Permitted)
- **Refresh JWKS Public Key Cache**: `refresh_jwks_cache()` (Risk: Low).
- **Restart Redis Session Cache Replica**: (Risk: Low if cluster mode enabled).

### Risky Actions (HUMAN APPROVAL REQUIRED)
- **Force Invalidate All User Sessions**: `invalidate_all_sessions()` (Risk: High. Forces all company employees to re-login).
- **Restart Auth Core Service**: `restart_service(service="auth-service")` (Risk: High).

## Verification Step
1. Probe `/auth/health` endpoint.
2. Issue a test JWT verification request. Status must be 200 OK.

