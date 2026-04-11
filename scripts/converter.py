"""
Conversion automator: replied → meeting_booked → (won/lost).

When a lead has status=replied:
  1. Tries to trigger n8n meeting-booking workflow (if configured)
  2. Creates a PaperClip issue so the CMO agent tracks it
  3. Sends a warm reply via email suggesting a calendar link

Run after reply_tracker.py in the pipeline.
"""
import sys
from datetime import datetime, timezone

try:
    import requests as _req
    _HTTP_OK = True
except ImportError:
    _HTTP_OK = False

from config import (
    HUB_URL, HUB_API_KEY,
    N8N_BASE, N8N_MEETING_WF,
    PAPERCLIP_URL, PAPERCLIP_COMPANY_ID, PAPERCLIP_AGENT_CMO,
    GMAIL_ACCOUNT, GMAIL_KEYRING_PASSWORD,
)
from leads import load_leads, save_leads
from senders import send_email
from utils import parse_display_name

CALENDLY_LINK = "https://calendly.com/berkahkarya/15min"   # update with real link
MEETING_SUBJECT = "Let's Connect — BerkahKarya x {name}"

_HEADERS = {"Content-Type": "application/json"}
if HUB_API_KEY:
    _HEADERS["X-Api-Key"] = HUB_API_KEY

_PAPER_HEADERS = {"Content-Type": "application/json"}


def _n8n_trigger(lead_name: str, email: str, vertical: str) -> bool:
    """Trigger n8n meeting workflow if configured."""
    if not N8N_MEETING_WF or not _HTTP_OK:
        return False
    url = f"{N8N_BASE}/{N8N_MEETING_WF}"
    try:
        r = _req.post(url, json={
            "lead_name": lead_name,
            "email": email,
            "vertical": vertical,
            "calendly": CALENDLY_LINK,
            "source": "1ai-engage",
        }, timeout=10)
        if r.status_code < 300:
            print(f"  [n8n] Meeting workflow triggered for {lead_name}")
            return True
        print(f"  [n8n] Workflow error: {r.status_code}", file=sys.stderr)
    except Exception as e:
        print(f"  [n8n] Failed: {e}", file=sys.stderr)
    return False


def _paperclip_create_issue(lead_name: str, email: str, vertical: str, phone: str) -> bool:
    """Create a PaperClip issue so the CMO agent can track this lead."""
    if not _HTTP_OK:
        return False
    url = f"{PAPERCLIP_URL}/api/companies/{PAPERCLIP_COMPANY_ID}/issues"
    payload = {
        "title":       f"Hot Lead: {lead_name} replied to outreach",
        "description": (
            f"**Lead:** {lead_name}\n"
            f"**Vertical:** {vertical}\n"
            f"**Email:** {email}\n"
            f"**Phone:** {phone or 'N/A'}\n"
            f"**Status:** Replied to BerkahKarya cold outreach\n"
            f"**Next step:** Schedule discovery call via {CALENDLY_LINK}\n"
            f"**Source:** 1ai-engage pipeline\n"
            f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        ),
        "priority":    "high",
        "assignee_id": PAPERCLIP_AGENT_CMO,
        "labels":      ["hot-lead", "outreach", "discovery-call"],
    }
    try:
        r = _req.post(url, json=payload, headers=_PAPER_HEADERS, timeout=10)
        if r.status_code < 300:
            print(f"  [paperclip] Issue created for {lead_name}")
            return True
        print(f"  [paperclip] Error {r.status_code}: {r.text[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"  [paperclip] Failed: {e}", file=sys.stderr)
    return False


def _send_meeting_email(lead_name: str, email: str, vertical: str) -> bool:
    """Send warm reply with calendar link."""
    subject = MEETING_SUBJECT.format(name=lead_name)
    body = (
        f"Hi {lead_name.split('@')[0].split()[0]},\n\n"
        f"Thank you so much for getting back to me — I'm really glad to hear from you!\n\n"
        f"I'd love to learn more about what you're working on at {vertical} "
        f"and share some ideas on how AI automation could specifically help your team.\n\n"
        f"Would you be open to a quick 15-minute call? You can pick any time that works for you here:\n"
        f"👉 {CALENDLY_LINK}\n\n"
        f"Looking forward to connecting!\n\n"
        f"Best,\nVilona\nBerkahKarya\n"
        f"AI Automation · Digital Marketing · Software Dev\n"
        f"berkahkarya.org"
    )
    return send_email(email, subject, body)


def process_replied_leads() -> None:
    """
    For every lead with status=replied that hasn't been converted yet:
    1. Send meeting email with calendar link
    2. Trigger n8n workflow (if configured)
    3. Create PaperClip issue
    4. Mark status as meeting_booked (optimistically — we sent the invite)
    """
    df = load_leads()
    if df is None:
        return

    replied = df[df["status"] == "replied"]
    if replied.empty:
        print("No replied leads to convert.")
        return

    print(f"Processing {len(replied)} replied leads for conversion...")
    converted = 0

    for index, row in replied.iterrows():
        name     = parse_display_name(row.get("displayName"))
        email    = str(row.get("email") or "").strip()
        phone    = str(row.get("internationalPhoneNumber") or row.get("phone") or "").strip()
        vertical = str(row.get("type") or row.get("primaryType") or "Business")

        if not email or email.lower() in ("nan", "none", ""):
            print(f"  [skip] {name} — no email for conversion.")
            continue

        print(f"\n  Converting: {name} ({vertical})")

        # 1. Send warm reply with calendar link
        sent = _send_meeting_email(name, email, vertical)

        # 2. n8n automation (non-blocking)
        _n8n_trigger(name, email, vertical)

        # 3. PaperClip issue (non-blocking)
        _paperclip_create_issue(name, email, vertical, phone)

        if sent:
            df.at[index, "status"] = "meeting_booked"
            converted += 1
            print(f"  ✅ Meeting invite sent to {name}")

    save_leads(df)
    print(f"\nConversion complete. {converted} leads sent meeting invites.")


if __name__ == "__main__":
    process_replied_leads()
