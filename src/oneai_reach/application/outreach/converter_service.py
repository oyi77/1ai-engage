from datetime import datetime, timezone
from typing import Optional

try:
    import requests as _req
    _HTTP_OK = True
except ImportError:
    _HTTP_OK = False

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

CALENDLY_LINK = "https://calendly.com/berkahkarya/15min"
MEETING_SUBJECT = "Let's Connect — BerkahKarya x {name}"


class ConverterService:

    def __init__(self, config: Settings):
        self.config = config
        self.calendly_link = config.booking.calendly_link or CALENDLY_LINK
        self.n8n_base = config.n8n.base
        self.n8n_meeting_wf = config.n8n.meeting_wf
        self.paperclip_url = config.paperclip.url
        self.paperclip_company_id = config.paperclip.company_id
        self.paperclip_agent_cmo = config.paperclip.agent_cmo
        self.telegram_bot_token = config.telegram.bot_token
        self.telegram_chat_id = config.telegram.chat_id
        self.waha_url = config.waha.url
        self.waha_direct_url = config.waha.direct_url
        self.waha_api_key = config.waha.api_key
        self.waha_direct_api_key = config.waha.direct_api_key
        self.waha_session = config.waha.session
        self.waha_own_number = config.waha.own_number

    def process_replied_leads(self, df, send_email_fn, parse_display_name_fn, is_empty_fn, save_leads_fn) -> int:
        replied = df[df["status"] == "replied"]
        if replied.empty:
            logger.info("No replied leads to convert")
            return 0

        logger.info(f"Processing {len(replied)} replied leads for conversion")
        converted = 0

        for index, row in replied.iterrows():
            name = parse_display_name_fn(row.get("displayName"))
            email = str(row.get("email") or "").strip()
            phone = str(row.get("internationalPhoneNumber") or row.get("phone") or "").strip()
            vertical = str(row.get("type") or row.get("primaryType") or "Business")

            if is_empty_fn(email):
                logger.info(f"[skip] {name} — no email for conversion")
                continue

            logger.info(f"Converting: {name} ({vertical})")

            sent = self._send_meeting_email(name, email, vertical, send_email_fn)
            self._notify_team(name, email, vertical, phone)
            self._n8n_trigger(name, email, vertical)
            self._paperclip_create_issue(name, email, vertical, phone)

            if sent:
                df.at[index, "status"] = "meeting_booked"
                converted += 1
                logger.info(f"✅ Meeting invite sent to {name}")

        save_leads_fn(df)
        logger.info(f"Conversion complete. {converted} leads sent meeting invites")
        return converted

    def _send_meeting_email(self, lead_name: str, email: str, vertical: str, send_email_fn) -> bool:
        subject = MEETING_SUBJECT.format(name=lead_name)
        body = (
            f"Hi {lead_name.split('@')[0].split()[0]},\n\n"
            f"Thank you so much for getting back to me — I'm really glad to hear from you!\n\n"
            f"I'd love to learn more about what you're working on at {vertical} "
            f"and share some ideas on how AI automation could specifically help your team.\n\n"
            f"Would you be open to a quick 15-minute call? You can pick any time that works for you here:\n"
            f"👉 {self.calendly_link}\n\n"
            f"Looking forward to connecting!\n\n"
            f"Best,\nVilona\nBerkahKarya\n"
            f"AI Automation · Digital Marketing · Software Dev\n"
            f"berkahkarya.org"
        )
        return send_email_fn(email, subject, body)

    def _n8n_trigger(self, lead_name: str, email: str, vertical: str) -> bool:
        if not self.n8n_meeting_wf or not _HTTP_OK:
            return False
        url = f"{self.n8n_base}/{self.n8n_meeting_wf}"
        try:
            r = _req.post(
                url,
                json={
                    "lead_name": lead_name,
                    "email": email,
                    "vertical": vertical,
                    "calendly": self.calendly_link,
                    "source": "1ai-reach",
                },
                timeout=10,
            )
            if r.status_code < 300:
                logger.info(f"[n8n] Meeting workflow triggered for {lead_name}")
                return True
            logger.error(f"[n8n] Workflow error: {r.status_code}")
        except Exception as e:
            logger.error(f"[n8n] Failed: {e}")
        return False

    def _notify_team(self, lead_name: str, email: str, vertical: str, phone: str) -> None:
        if not _HTTP_OK:
            return
        now = datetime.now().strftime("%d %b %Y %H:%M WIB")
        tg_msg = (
            f"🔥 *HOT LEAD — 1ai-reach*\n\n"
            f"👤 *{lead_name}*\n"
            f"💼 {vertical}\n"
            f"📧 {email}\n"
            f"📱 {phone or 'N/A'}\n\n"
            f"📅 {self.calendly_link}\n"
            f"⏰ {now}"
        )
        wa_msg = (
            f"🔥 *HOT LEAD!*\n"
            f"{lead_name} ({vertical}) balas email outreach kita!\n"
            f"Email: {email}\n"
            f"Book meeting: {self.calendly_link}"
        )
        try:
            r = _req.post(
                f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage",
                json={"chat_id": self.telegram_chat_id, "text": tg_msg, "parse_mode": "Markdown"},
                timeout=10,
            )
            if r.status_code < 300:
                logger.info("[telegram] Team notified")
            else:
                logger.error(f"[telegram] Error {r.status_code}: {r.text[:100]}")
        except Exception as e:
            logger.error(f"[telegram] Failed: {e}")

        if self.waha_own_number:
            clean = "".join(filter(str.isdigit, self.waha_own_number))
            sent = False
            for target_name, base_url, headers in self._waha_targets():
                try:
                    r = _req.post(
                        f"{base_url}/api/sendText",
                        json={"chatId": f"{clean}@c.us", "text": wa_msg, "session": self.waha_session},
                        headers=headers,
                        timeout=10,
                    )
                    if r.status_code < 300:
                        logger.info(f"[whatsapp] Team notified via {target_name}")
                        sent = True
                        break
                except Exception as e:
                    logger.error(f"[whatsapp] {target_name} alert failed: {e}")
            if not sent:
                logger.error("[whatsapp] Team alert failed")

    def _paperclip_create_issue(self, lead_name: str, email: str, vertical: str, phone: str) -> bool:
        if not _HTTP_OK:
            return False
        url = f"{self.paperclip_url}/api/companies/{self.paperclip_company_id}/issues"
        payload = {
            "title": f"Hot Lead: {lead_name} replied to outreach",
            "description": (
                f"**Lead:** {lead_name}\n"
                f"**Vertical:** {vertical}\n"
                f"**Email:** {email}\n"
                f"**Phone:** {phone or 'N/A'}\n"
                f"**Status:** Replied to BerkahKarya cold outreach\n"
                f"**Next step:** Schedule discovery call via {self.calendly_link}\n"
                f"**Source:** 1ai-reach pipeline\n"
                f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            ),
            "priority": "high",
            "assignee_id": self.paperclip_agent_cmo,
            "labels": ["hot-lead", "outreach", "discovery-call"],
        }
        try:
            r = _req.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            if r.status_code < 300:
                logger.info(f"[paperclip] Issue created for {lead_name}")
                return True
            logger.error(f"[paperclip] Error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            logger.error(f"[paperclip] Failed: {e}")
        return False

    def _waha_targets(self):
        targets = []
        seen = set()
        for name, base_url, api_key in [
            ("WAHA", self.waha_url, self.waha_api_key),
            ("WAHA_DIRECT", self.waha_direct_url, self.waha_direct_api_key),
        ]:
            url = str(base_url or "").rstrip("/")
            key = str(api_key or "")
            if not url or (url, key) in seen:
                continue
            seen.add((url, key))
            targets.append((name, url, {"X-Api-Key": key, "Content-Type": "application/json"}))
        return targets
