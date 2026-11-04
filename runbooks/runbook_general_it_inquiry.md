# Runbook: General Enterprise IT Inquiry & Access Requests
**Service**: `enterprise-it`  
**Category**: `GENERAL_IT`  
**Default Severity**: `P4_LOW`  

## 1. Overview
Standard operating procedures for non-incident IT inquiries, including VPN setup, MFA resets, corporate Wi-Fi credentials, and developer workstation onboarding.

## 2. Common Topics & Resolutions
- **GlobalProtect VPN Setup**: Download the enterprise client from `https://vpn.enterprise.io`. Connect using your Okta SSO identity and hardware MFA key.
- **MFA Token Desync**: Navigate to `https://id.enterprise.io/self-service/mfa` to re-enroll your authenticator app.
- **SSH Key Onboarding**: Submit public ed25519 keys via the internal developer portal at `https://dev.enterprise.io/keys`.
- **Corporate Web Filtering & Blocked Websites (e.g. YouTube, Streaming Media)**:
  - Video streaming platforms (including `youtube.com`) and social media are restricted by default on corporate networks and VPN under the Enterprise Acceptable Use & Content Filtering Policy (enforced by Zscaler / Corporate Firewall).
  - This is an intentional security and bandwidth management policy, NOT an IT infrastructure failure.
  - **Business Exception Procedure**: If YouTube access is required for legitimate job functions (e.g., watching developer tech talks, official product tutorials, or marketing):
    1. Navigate to the IT Self-Service Portal at `https://it.enterprise.io/requests/url-exception`.
    2. Fill out the "Web Category Exception" form and provide business justification.
    3. Include your direct manager's email for automated approval.
    4. IT Network Security will provision the policy exception within 24 hours of approval.

## 3. Autonomous Handling
- These requests do **NOT** require infrastructure remediation or service restarts.
- The agent should answer with direct documentation citations and mark severity as `P4_LOW`.

