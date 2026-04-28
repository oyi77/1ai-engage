"""Automated performance reports - weekly/monthly email reports.

Generates and emails stakeholder reports with:
- Pipeline metrics (leads, conversion rates)
- Channel performance (email vs WhatsApp)
- Revenue attribution
- Deliverability stats
- Week-over-week trends
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger
from oneai_reach.infrastructure.messaging.email_sender import EmailSender

logger = get_logger(__name__)


class ReportGenerator:
    """Generates automated performance reports."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.reports_dir = Path(config.database.data_dir) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_weekly_report(self, df, start_date: datetime, end_date: datetime) -> Dict:
        """Generate weekly performance report."""
        return self._generate_period_report(df, start_date, end_date, "weekly")
    
    def generate_monthly_report(self, df, start_date: datetime, end_date: datetime) -> Dict:
        """Generate monthly performance report."""
        return self._generate_period_report(df, start_date, end_date, "monthly")
    
    def _generate_period_report(self, df, start_date: datetime, end_date: datetime, report_type: str) -> Dict:
        """Generate report for a specific period."""
        # Filter by date range
        mask = (df["created_at"] >= start_date.isoformat()) & (df["created_at"] <= end_date.isoformat())
        period_df = df[mask]
        
        # Pipeline metrics
        total_leads = len(period_df)
        contacted = len(period_df[period_df["status"] == "contacted"])
        replied = len(period_df[period_df["status"] == "replied"])
        meeting_booked = len(period_df[period_df["status"] == "meeting_booked"])
        won = len(period_df[period_df["status"] == "won"])
        
        # Conversion rates
        contact_rate = (contacted / total_leads * 100) if total_leads > 0 else 0
        reply_rate = (replied / contacted * 100) if contacted > 0 else 0
        meeting_rate = (meeting_booked / replied * 100) if replied > 0 else 0
        win_rate = (won / meeting_booked * 100) if meeting_booked > 0 else 0
        
        # Channel performance
        email_sent = len(period_df[period_df["email_sent"] == True]) if "email_sent" in period_df.columns else 0
        whatsapp_sent = len(period_df[period_df["whatsapp_sent"] == True]) if "whatsapp_sent" in period_df.columns else 0
        
        report = {
            "report_type": report_type,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": {
                "total_leads": total_leads,
                "contacted": contacted,
                "replied": replied,
                "meeting_booked": meeting_booked,
                "won": won,
            },
            "conversion_rates": {
                "contact_rate": f"{contact_rate:.1f}%",
                "reply_rate": f"{reply_rate:.1f}%",
                "meeting_rate": f"{meeting_rate:.1f}%",
                "win_rate": f"{win_rate:.1f}%",
            },
            "channel_performance": {
                "email_sent": email_sent,
                "whatsapp_sent": whatsapp_sent,
            },
        }
        
        # Save report
        report_file = self.reports_dir / f"{report_type}_{start_date.strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def format_report_email(self, report: Dict) -> str:
        """Format report as email body."""
        return f"""
Performance Report - {report['report_type'].title()}
Period: {report['period']}
Generated: {report['generated_at'][:10]}

PIPELINE SUMMARY
────────────────────────────────
Total Leads: {report['pipeline']['total_leads']:,}
Contacted: {report['pipeline']['contacted']:,}
Replied: {report['pipeline']['replied']:,}
Meeting Booked: {report['pipeline']['meeting_booked']:,}
Won: {report['pipeline']['won']:,}

CONVERSION RATES
────────────────────────────────
Contact Rate: {report['conversion_rates']['contact_rate']}
Reply Rate: {report['conversion_rates']['reply_rate']}
Meeting Rate: {report['conversion_rates']['meeting_rate']}
Win Rate: {report['conversion_rates']['win_rate']}

CHANNEL PERFORMANCE
────────────────────────────────
Email Sent: {report['channel_performance']['email_sent']:,}
WhatsApp Sent: {report['channel_performance']['whatsapp_sent']:,}

────────────────────────────────
Report saved to: {self.reports_dir}
"""


class ReportScheduler:
    """Schedules and sends automated reports."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.generator = ReportGenerator(config)
        self.email_sender = EmailSender(config)
    
    def send_weekly_report(self, df, recipients: List[str]):
        """Generate and send weekly report."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        report = self.generator.generate_weekly_report(df, start_date, end_date)
        email_body = self.generator.format_report_email(report)
        
        for recipient in recipients:
            self.email_sender.send(
                email=recipient,
                subject=f"Weekly Performance Report - {end_date.strftime('%Y-%m-%d')}",
                body=email_body.strip()
            )
        
        logger.info(f"Weekly report sent to {len(recipients)} recipients")
    
    def send_monthly_report(self, df, recipients: List[str]):
        """Generate and send monthly report."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        report = self.generator.generate_monthly_report(df, start_date, end_date)
        email_body = self.generator.format_report_email(report)
        
        for recipient in recipients:
            self.email_sender.send(
                email=recipient,
                subject=f"Monthly Performance Report - {end_date.strftime('%Y-%m')}",
                body=email_body.strip()
            )
        
        logger.info(f"Monthly report sent to {len(recipients)} recipients")


def get_report_scheduler(config: Settings) -> ReportScheduler:
    """Get or create report scheduler."""
    return ReportScheduler(config)
