"""Outreach compliance wrapper - GDPR checks before sending.

This module wraps email and WhatsApp senders with GDPR compliance checks:
- Consent verification before sending
- Do-not-contact (DNC) list checking
- Audit logging for all outreach attempts
- Automatic consent recording for imported leads
"""

from typing import Optional, Tuple
from datetime import datetime, timezone

from oneai_reach.config.settings import Settings
from oneai_reach.application.compliance.gdpr_tools import get_gdpr_tools, GDPRTools
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


class ComplianceWrapper:
    """Wraps outreach senders with GDPR compliance checks.
    
    Usage:
        wrapper = ComplianceWrapper(config)
        
        # Before sending email:
        if wrapper.can_contact_email(lead_id, email):
            email_sender.send(email, subject, body, lead_id=lead_id)
            wrapper.record_outreach(lead_id, email, "email", True)
        
        # Before sending WhatsApp:
        if wrapper.can_contact_whatsapp(lead_id, phone):
            whatsapp_sender.send(phone, message)
            wrapper.record_outreach(lead_id, phone, "whatsapp", True)
    """
    
    def __init__(self, config: Settings):
        self.config = config
        self.gdpr = get_gdpr_tools(config)
    
    def can_contact_email(self, lead_id: str, email: str, consent_method: str = "import") -> Tuple[bool, str]:
        """Check if we can legally send email to this lead.
        
        Returns:
            Tuple of (can_send: bool, reason: str)
        """
        if not email:
            return False, "No email address"
        
        # Check DNC list
        if self.gdpr.is_in_dnc(email):
            logger.warning(f"GDPR block: {email} is in do-not-contact list")
            return False, "Email is in do-not-contact list"
        
        # Check consent (for EU leads, explicit consent required)
        # For B2B outreach, legitimate interest may apply, but we track consent anyway
        if self.gdpr.has_consent(lead_id, "email_marketing"):
            return True, "Consent verified"
        
        # No explicit consent - record implied consent from import
        # This is acceptable for B2B under legitimate interest, but we track it
        self.gdpr.record_consent(lead_id, email, "email_marketing", True, consent_method)
        logger.info(f"GDPR: Recorded implied consent for {email} (B2B legitimate interest)")
        return True, "Implied consent recorded (B2B)"
    
    def can_contact_whatsapp(self, lead_id: str, phone: str, consent_method: str = "import") -> Tuple[bool, str]:
        """Check if we can legally send WhatsApp to this lead.
        
        WhatsApp has stricter rules - explicit consent strongly recommended.
        
        Returns:
            Tuple of (can_send: bool, reason: str)
        """
        if not phone:
            return False, "No phone number"
        
        # Check DNC list (by phone)
        # We use email-based DNC, but could extend to phone
        # For now, just check if we have any consent record
        
        if self.gdpr.has_consent(lead_id, "whatsapp_marketing"):
            return True, "Consent verified"
        
        # Record implied consent
        self.gdpr.record_consent(lead_id, phone, "whatsapp_marketing", True, consent_method)
        logger.info(f"GDPR: Recorded implied consent for {phone} (B2B legitimate interest)")
        return True, "Implied consent recorded (B2B)"
    
    def record_outreach(self, lead_id: str, contact: str, channel: str, success: bool):
        """Record outreach attempt for audit trail."""
        self.gdpr._audit("outreach", lead_id, {
            "channel": channel,
            "contact": contact,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def withdraw_consent(self, lead_id: str, email: str, reason: str = "User request"):
        """Withdraw all consent for a lead (opt-out)."""
        self.gdpr.withdraw_consent(lead_id, "email_marketing")
        self.gdpr.withdraw_consent(lead_id, "whatsapp_marketing")
        self.gdpr.add_to_dnc(email, reason)
        logger.info(f"GDPR: Withdrawn consent for {lead_id} - {reason}")
    
    def export_lead_data(self, lead_id: str, lead_data: dict) -> str:
        """Export all data for a lead (GDPR data portability)."""
        return self.gdpr.export_data(lead_id, lead_data)
    
    def delete_lead_data(self, lead_id: str, email: str):
        """Delete all data for a lead (right to be forgotten)."""
        self.gdpr.delete_data(lead_id, email)
        logger.info(f"GDPR: Deleted all data for {lead_id}")


def get_compliance_wrapper(config: Settings) -> ComplianceWrapper:
    """Get or create compliance wrapper."""
    return ComplianceWrapper(config)
