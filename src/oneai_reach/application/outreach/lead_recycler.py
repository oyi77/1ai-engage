"""Lead recycling - re-engage cold leads after 30-60 days.

Identifies leads that went cold (no response after initial contact)
and re-engages them with fresh messaging based on:
- Time-based triggers (30, 60, 90 days)
- New case studies in their industry
- Product updates or new offerings
- Seasonal relevance
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger
from oneai_reach.application.content.case_study_matcher import get_case_study_matcher

logger = get_logger(__name__)


class LeadRecycler:
    """Identifies and re-engages cold leads."""
    
    RECYCLE_INTERVALS = [30, 60, 90]  # Days after initial contact
    
    def __init__(self, config: Settings):
        self.config = config
        self.case_study_matcher = get_case_study_matcher(config)
    
    def find_cold_leads(self, df: pd.DataFrame, days_since_contact: int = 30) -> pd.DataFrame:
        """Find leads that went cold after initial contact.
        
        Args:
            df: Leads DataFrame
            days_since_contact: Minimum days since last contact
        
        Returns:
            DataFrame of cold leads eligible for recycling
        """
        cold_leads = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_since_contact)
        
        for idx, row in df.iterrows():
            contacted_at = row.get("contacted_at")
            status = str(row.get("status") or "")
            
            # Skip if already in active pipeline
            if status in ("replied", "meeting_booked", "won", "negotiation"):
                continue
            
            # Skip if no contact date
            if not contacted_at or str(contacted_at) == "nan":
                continue
            
            try:
                contact_date = datetime.fromisoformat(str(contacted_at)).replace(tzinfo=timezone.utc)
                if contact_date < cutoff and status == "contacted":
                    cold_leads.append(row)
            except Exception:
                continue
        
        return pd.DataFrame(cold_leads) if cold_leads else pd.DataFrame()
    
    def prioritize_cold_leads(self, cold_leads: pd.DataFrame) -> List[Tuple[str, int, str]]:
        """Prioritize cold leads by recycle interval and score.
        
        Returns:
            List of (lead_id, days_since_contact, priority_reason)
        """
        prioritized = []
        now = datetime.now(timezone.utc)
        
        for idx, row in cold_leads.iterrows():
            contacted_at = row.get("contacted_at")
            if not contacted_at:
                continue
            
            try:
                contact_date = datetime.fromisoformat(str(contacted_at)).replace(tzinfo=timezone.utc)
                days_since = (now - contact_date).days
                
                # Determine recycle interval
                interval = None
                for days in self.RECYCLE_INTERVALS:
                    if days_since >= days and days_since < days + 15:
                        interval = days
                        break
                
                if interval:
                    lead_id = str(row.get("id") or f"lead_{idx}")
                    priority = "high" if interval == 30 else "medium" if interval == 60 else "low"
                    prioritized.append((lead_id, days_since, priority))
            
            except Exception:
                continue
        
        # Sort by priority (30 days first, then 60, then 90)
        prioritized.sort(key=lambda x: x[1])
        return prioritized
    
    def generate_reengagement_message(self, lead_row: pd.Series, interval: int) -> str:
        """Generate personalized re-engagement message.
        
        Args:
            lead_row: Lead data
            interval: Days since initial contact (30, 60, or 90)
        
        Returns:
            Re-engagement message
        """
        company = str(lead_row.get("company_name") or "your company")
        vertical = str(lead_row.get("vertical") or "")
        
        # Get relevant case study
        case_studies = self.case_study_matcher.match({"vertical": vertical})
        case_study = case_studies[0] if case_studies else None
        
        if interval == 30:
            # Gentle follow-up
            message = f"""Hi! Following up on our previous message about helping {company} with digital transformation.

We recently helped a {vertical or 'similar'} company achieve impressive results. Would you be open to a quick 15-min chat next week?

Best regards,
BerkahKarya Team"""
        
        elif interval == 60:
            # Social proof angle
            if case_study:
                message = f"""Hi! Wanted to share a quick win - we just helped {case_study.get('company', 'a client')} in {vertical or 'your industry'} achieve {case_study.get('result', 'great results')}.

Thought of {company} as you might have similar opportunities. Worth a conversation?

Best,
BerkahKarya Team"""
            else:
                message = f"""Hi! Checking in - we've been helping companies like {company} streamline their operations and reduce costs.

Any interest in exploring how we could help? Happy to share specific examples.

Best,
BerkahKarya Team"""
        
        else:  # 90 days
            # Break-up message
            message = f"""Hi! This will be my last attempt to reach out.

If digital transformation isn't a priority right now, no worries at all. Just let me know and I'll close your file.

If you ARE interested, I'd love to connect. Either way, wish you all the best!

Regards,
BerkahKarya Team"""
        
        return message
    
    def recycle_lead(self, lead_row: pd.Series, send_fn, interval: int) -> bool:
        """Send re-engagement message to a cold lead.
        
        Args:
            lead_row: Lead data
            send_fn: Function to send message (email or WhatsApp)
            interval: Days since initial contact
        
        Returns:
            True if sent successfully
        """
        email = str(lead_row.get("email") or "").strip()
        phone = str(lead_row.get("internationalPhoneNumber") or "").strip()
        lead_id = str(lead_row.get("id") or "")
        
        message = self.generate_reengagement_message(lead_row, interval)
        
        # Try email first, then WhatsApp
        sent = False
        if email:
            sent = send_fn(email, f"Following up - {lead_row.get('company_name', '')}", message, lead_id=lead_id)
        
        if not sent and phone:
            sent = send_fn(phone, message)
        
        if sent:
            logger.info(f"Re-engaged lead {lead_id} after {interval} days")
        
        return sent
    
    def run_recycling_cycle(self, df: pd.DataFrame, send_fn) -> Dict:
        """Run full recycling cycle on all cold leads.
        
        Args:
            df: Leads DataFrame
            send_fn: Function to send messages
        
        Returns:
            Summary of recycling results
        """
        results = {"total_cold": 0, "re_engaged": 0, "by_interval": {}}
        
        for interval in self.RECYCLE_INTERVALS:
            cold_leads = self.find_cold_leads(df, days_since_contact=interval)
            results["total_cold"] += len(cold_leads)
            results["by_interval"][interval] = 0
            
            prioritized = self.prioritize_cold_leads(cold_leads)
            
            for lead_id, days_since, priority in prioritized:
                # Find the lead row
                lead_row = df[df["id"] == lead_id].iloc[0] if "id" in df.columns else df.iloc[0]
                
                if self.recycle_lead(lead_row, send_fn, interval):
                    results["re_engaged"] += 1
                    results["by_interval"][interval] += 1
        
        logger.info(f"Recycling complete: {results['re_engaged']}/{results['total_cold']} leads re-engaged")
        return results


def get_lead_recycler(config: Settings) -> LeadRecycler:
    """Get or create lead recycler."""
    return LeadRecycler(config)
