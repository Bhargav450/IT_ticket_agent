import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def _get_headers():
    token = (settings.ZAMMAD_TOKEN or "").strip().strip('"').strip("'")
    return {
        "Authorization": f"Token token={token}",
        "Content-Type": "application/json"
    }

def _get_url():
    url = (settings.ZAMMAD_URL or "http://localhost:8080").strip().strip('"').strip("'")
    return url.rstrip("/")

def create_zammad_ticket(title: str, description: str, reporter_email: str) -> dict:
    """Creates a new ticket in Zammad using the reporter_email directly from the request body."""
    url = _get_url()
    headers = _get_headers()

    # ── Startup diagnostics (always printed, flush=True forces immediate output) ─
    print(f"[ZAMMAD] create_zammad_ticket called", flush=True)
    print(f"[ZAMMAD] URL        : {url}", flush=True)
    print(f"[ZAMMAD] TOKEN set  : {bool(settings.ZAMMAD_TOKEN)}", flush=True)
    print(f"[ZAMMAD] Email      : {reporter_email}", flush=True)
    # ─────────────────────────────────────────────────────────────────────────

    if not settings.ZAMMAD_TOKEN:
        print("❌ [ZAMMAD] ZAMMAD_TOKEN is NOT set — skipping ticket creation. Check your .env file!", flush=True)
        return {}

    # Normalize email to lowercase
    email = (reporter_email or "").strip().lower()
    

    payload = {
        "title": title,
        "group": "Users",
        "customer": email,
        "article": {
            "subject": title,
            "body": description,
            "type": "note",
            "internal": False
        }
    }
    
    try:
        res = httpx.post(f"{url}/api/v1/tickets", json=payload, headers=headers, timeout=10.0)
        if res.status_code in (200, 201):
            data = res.json()
            print(f"✅ Zammad ticket #{data.get('number')} created (ID: {data.get('id')}) for customer: {email}")
            return data
        
        # If customer does not exist in Zammad yet, auto-register them and retry
        if res.status_code in (400, 422) and "customer" in res.text.lower():
            username = email.split("@")[0].capitalize()
            user_payload = {
                "firstname": username,
                "lastname": "User",
                "email": email,
                "roles": ["Customer"]
            }
            user_res = httpx.post(f"{url}/api/v1/users", json=user_payload, headers=headers, timeout=10.0)
            if user_res.status_code in (200, 201):
                retry = httpx.post(f"{url}/api/v1/tickets", json=payload, headers=headers, timeout=10.0)
                if retry.status_code in (200, 201):
                    data = retry.json()
                    print(f"✅ Zammad ticket #{data.get('number')} created for new customer: {email}")
                    return data
                print(f"❌ Zammad creation retry error: {retry.status_code} - {retry.text}")
            else:
                print(f"❌ Could not auto-create customer in Zammad: {user_res.status_code} - {user_res.text}")
        else:
            print(f"❌ Zammad ticket creation error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Could not connect to Zammad: {e}")
    return {}

def update_zammad_ticket(zammad_ticket_id: int, status: str, resolution_note: str) -> dict:
    """Updates and closes the Zammad ticket when resolved."""
    url = _get_url()
    headers = _get_headers()
    
    if not settings.ZAMMAD_TOKEN:
        return {}

    state_map = {
        "RESOLVED": "closed",
        "AWAITING_APPROVAL": "open",
        "INVESTIGATING": "open",
    }
    payload = {
        "state": state_map.get(status, "open"),
        "article": {
            "subject": "Agent Resolution",
            "body": resolution_note,
            "type": "note",
            "internal": False
        }
    }
    try:
        res = httpx.put(f"{url}/api/v1/tickets/{zammad_ticket_id}", json=payload, headers=headers, timeout=10.0)
        if res.status_code in (200, 201):
            print(f"✅ Zammad ticket #{zammad_ticket_id} updated to {payload['state']}")
            return res.json()
        print(f"❌ Zammad ticket update error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Failed to update Zammad ticket {zammad_ticket_id}: {e}")
    return {}
