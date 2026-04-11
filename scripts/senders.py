import os
import subprocess
import sys

try:
    import requests as _req
    _HTTP_OK = True
except ImportError:
    _HTTP_OK = False

from config import (
    GMAIL_ACCOUNT, GMAIL_KEYRING_PASSWORD, LOGS_DIR,
    WAHA_URL, WAHA_API_KEY, WAHA_SESSION,
)

EMAIL_QUEUE_LOG = str(LOGS_DIR / "email_queue.log")

_WAHA_HEADERS = {"X-Api-Key": WAHA_API_KEY, "Content-Type": "application/json"}


def _send_wa_waha(phone: str, message: str) -> bool:
    """Primary: send WhatsApp via WAHA HTTP API."""
    if not _HTTP_OK:
        return False
    clean = "".join(filter(str.isdigit, str(phone)))
    if not clean.startswith("62"):
        clean = "62" + clean.lstrip("0")
    chat_id = f"{clean}@c.us"
    url = f"{WAHA_URL}/api/sendText"
    try:
        r = _req.post(url, json={
            "chatId":  chat_id,
            "text":    message,
            "session": WAHA_SESSION,
        }, headers=_WAHA_HEADERS, timeout=15)
        if r.status_code < 300:
            print(f"✅ WA sent via WAHA to {clean}")
            return True
        print(f"❌ WAHA error {r.status_code}: {r.text[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ WAHA failed: {e}", file=sys.stderr)
    return False


def _send_wa_wacli(phone: str, message: str) -> bool:
    """Fallback: send WhatsApp via wacli CLI."""
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    try:
        result = subprocess.run(
            ["wacli", "send", "text", "--to", clean_phone, "--message", message],
            capture_output=True, text=True,
        )
        if "not authenticated" in result.stderr:
            print("WA Error: wacli not authenticated. Run 'wacli auth'.")
            return False
        if result.returncode == 0:
            print(f"✅ WA sent via wacli to {clean_phone}")
            return True
        print(f"❌ wacli error: {result.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print("❌ wacli not found.", file=sys.stderr)
    return False


def send_whatsapp(phone: str, message: str) -> bool:
    if not phone or str(phone).lower() in ("nan", "none", ""):
        print("Skip WA: No phone number.")
        return False
    # Try WAHA first (HTTP API), fall back to wacli
    for name, fn in [("WAHA", _send_wa_waha), ("wacli", _send_wa_wacli)]:
        try:
            if fn(phone, message):
                return True
        except Exception as e:
            print(f"WA method {name} failed: {e}", file=sys.stderr)
    print(f"❌ All WA methods failed for {phone}")
    return False


def _send_via_gog(email: str, subject: str, body: str) -> bool:
    """Primary: send via gog Gmail CLI (free)."""
    print(f"Attempting email via gog to {email}...")
    env = {**os.environ, "GOG_KEYRING_PASSWORD": GMAIL_KEYRING_PASSWORD, "GOG_ACCOUNT": GMAIL_ACCOUNT}
    try:
        result = subprocess.run(
            ["gog", "gmail", "send", "--to", email, "--subject", subject, "--body", body],
            capture_output=True, text=True, timeout=30, env=env,
        )
        if result.returncode == 0:
            print(f"✅ Email sent via gog to {email}")
            return True
        print(f"❌ Gog error: {result.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Gog failed: {e}")
        return False


def _send_via_himalaya(email: str, subject: str, body: str) -> bool:
    """Fallback: send via himalaya IMAP/SMTP (free)."""
    print(f"Attempting email via himalaya to {email}...")
    template = f"To: {email}\nSubject: {subject}\n\n{body}"
    try:
        result = subprocess.run(
            ["himalaya", "template", "send"],
            input=template, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"✅ Email sent via himalaya to {email}")
            return True
        print(f"❌ Himalaya error: {result.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Himalaya failed: {e}")
        return False


def _send_via_mock(email: str, subject: str, body: str) -> bool:
    """Last resort: queue email locally for manual review (free, no send)."""
    print(f"[QUEUE] Email logged for {email} — review at {EMAIL_QUEUE_LOG}")
    os.makedirs(os.path.dirname(EMAIL_QUEUE_LOG), exist_ok=True)
    with open(EMAIL_QUEUE_LOG, "a") as f:
        f.write(f"\n---\nTo: {email}\nSubject: {subject}\nBody: {body}\n")
    return True


def send_email(email: str, subject: str, body: str) -> bool:
    if not email or str(email).lower() == "nan":
        print("Skip Email: No email address.")
        return False
    for name, method in [
        ("gog",      lambda: _send_via_gog(email, subject, body)),
        ("himalaya", lambda: _send_via_himalaya(email, subject, body)),
        ("queue",    lambda: _send_via_mock(email, subject, body)),
    ]:
        try:
            if method():
                return True
        except Exception as e:
            print(f"Method {name} failed: {e}")
    print(f"❌ All email methods failed for {email}")
    return False
