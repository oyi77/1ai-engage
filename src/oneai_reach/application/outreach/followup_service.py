import subprocess
from datetime import datetime, timezone

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

FOLLOWUP_DAYS = 7
SECOND_FOLLOWUP_DAYS = 14


class FollowupService:

    def __init__(self, config: Settings):
        self.config = config
        self.reviewer_model = config.llm.reviewer_model

    def send_followups(self, df, send_email_fn, parse_display_name_fn, is_empty_fn, save_leads_fn) -> tuple[int, int, int]:
        for col in ("status", "contacted_at", "followup_at"):
            if col not in df.columns:
                df[col] = None
            df[col] = df[col].astype(object)

        sent = 0
        skipped = 0
        cold_marked = 0

        for index, row in df.iterrows():
            status = str(row.get("status", ""))
            email = str(row.get("email", "")).strip()
            contacted_at = str(row.get("followup_at", "") or row.get("contacted_at", ""))

            if status not in ("contacted", "followed_up"):
                continue
            if is_empty_fn(email):
                continue
            if is_empty_fn(contacted_at):
                continue

            name = parse_display_name_fn(row.get("displayName"))
            business_type = str(row.get("type", "") or row.get("primaryType", "") or "Business")
            days_since_contact = self._days_since(contacted_at)

            original_contacted_at = str(row.get("contacted_at", ""))
            total_days = self._days_since(original_contacted_at) if original_contacted_at else days_since_contact

            if total_days >= SECOND_FOLLOWUP_DAYS and status == "followed_up":
                logger.info(f"[cold] {name} — no reply after {total_days:.0f} days. Marking cold")
                df.at[index, "status"] = "cold"
                cold_marked += 1
                continue

            if days_since_contact < FOLLOWUP_DAYS:
                skipped += 1
                continue

            is_second = status == "followed_up"
            subject_prefix = "Final Check-in" if is_second else "Following Up"
            subject = f"{subject_prefix}: Collaboration Proposal from BerkahKarya"

            logger.info(f"[followup{'#2' if is_second else '#1'}] {name} ({days_since_contact:.0f} days since last contact)")
            body = self._generate_followup(name, business_type, is_second)

            success = send_email_fn(email, subject, body)
            if success:
                df.at[index, "status"] = "followed_up"
                df.at[index, "followup_at"] = datetime.now(timezone.utc).isoformat()
                sent += 1

        save_leads_fn(df)
        logger.info(f"Follow-up complete: {sent} sent, {skipped} skipped, {cold_marked} marked cold")
        return sent, skipped, cold_marked

    def _generate_followup(self, name: str, business_type: str, is_second: bool = False) -> str:
        prompt = self._build_followup_prompt(name, business_type, is_second)
        try:
            result = subprocess.run(
                ["claude", "-p", "--model", self.reviewer_model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.error(f"Claude followup error: {e}")

        if is_second:
            return (
                f"Hi,\n\nI wanted to follow up one last time regarding our proposal for {name}.\n"
                f"I completely understand if now isn't the right time. "
                f"Feel free to reach out whenever you're ready to explore how AI automation can help your business grow.\n\n"
                f"Wishing you all the best,\nVilona\nBerkahKarya"
            )
        return (
            f"Hi,\n\nI hope this message finds you well. I wanted to gently follow up on the proposal I sent last week "
            f"regarding AI automation and digital marketing opportunities for {name}.\n\n"
            f"Many businesses like yours have seen significant efficiency gains and cost reductions with our solutions. "
            f"Would you be open to a quick 15-minute call this week?\n\n"
            f"Best regards,\nVilona\nBerkahKarya"
        )

    def _build_followup_prompt(self, name: str, business_type: str, is_second: bool) -> str:
        if is_second:
            return (
                f"Write a very short (3-4 sentences) final follow-up email.\n"
                f"Context: We sent a collaboration proposal to {name} ({business_type}) 2 weeks ago. No reply.\n"
                f"Sender: Vilona from BerkahKarya (AI Automation, Digital Marketing, Software Dev).\n"
                f"Tone: Warm, understanding, leave the door open. Not pushy.\n"
                f"End with: feel free to reach out anytime.\n"
                f"Output: just the email body, no subject line, no extra text."
            )
        return (
            f"Write a short (4-5 sentences) follow-up email.\n"
            f"Context: We sent a collaboration proposal to {name} ({business_type}) 1 week ago. No reply yet.\n"
            f"Sender: Vilona from BerkahKarya (AI Automation, Digital Marketing, Software Dev).\n"
            f"Tone: Friendly, helpful, not pushy. Reference AI automation as the key value.\n"
            f"Ask for a 15-minute call. Offer to share a quick case study.\n"
            f"Output: just the email body, no subject line, no extra text."
        )

    def _days_since(self, iso_str: str) -> float:
        try:
            dt = datetime.fromisoformat(str(iso_str)).replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except Exception:
            return 0
