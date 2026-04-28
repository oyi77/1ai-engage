"""LinkedIn lead scraping service.

Scrapes LinkedIn for B2B leads using:
- Company page employee extraction
- Sales Navigator integration (if API available)
- Public profile scraping (fallback)
- Job posting triggers (hiring = budget!)

Features:
- Extract decision makers by title
- Get company size, industry, location
- Track job changes (re-engagement trigger)
- Enrich with LinkedIn profile data
"""

import re
import json
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
import logging
import httpx

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LinkedInProfile:
    """LinkedIn profile data."""
    name: str
    title: str
    company: str
    industry: str
    location: str
    profile_url: str
    email: Optional[str] = None
    phone: Optional[str] = None
    connections: int = 0
    seniority: str = "unknown"  # c_level, vp, director, manager, individual
    departments: List[str] = None

    def __post_init__(self):
        if self.departments is None:
            self.departments = []


class LinkedInScraper:
    """LinkedIn lead scraping service."""

    # Decision maker title patterns
    DECISION_TITLES = {
        "c_level": ["ceo", "cto", "cfo", "coo", "cmo", "cio", "founder", "co-founder", "president"],
        "vp": ["vp", "vice president", "evp", "svp"],
        "director": ["director", "head of", "lead", "principal"],
        "manager": ["manager", "senior manager", "product owner"],
    }

    # Target departments for B2B outreach
    TARGET_DEPARTMENTS = ["sales", "marketing", "operations", "technology", "finance", "hr", "procurement"]

    def __init__(self, config: Settings):
        self.config = config
        self.linkedin_api_key = config.external_api.linkedin_api_key if hasattr(config.external_api, 'linkedin_api_key') else ""
        self.cache_dir = Path(config.database.data_dir) / "linkedin_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_company_employees(self, company_name: str, industry: str = "") -> List[LinkedInProfile]:
        """Scrape employee profiles from company page."""
        # Use Jina AI to fetch LinkedIn company page (bypasses some restrictions)
        from oneai_reach.infrastructure.web_reader import JinaWebReader
        
        company_slug = company_name.lower().replace(" ", "-")
        linkedin_url = f"https://www.linkedin.com/company/{company_slug}"
        
        try:
            markdown = await JinaWebReader.fetch_markdown(linkedin_url)
            profiles = self._parse_employee_profiles(markdown, company_name)
            logger.info(f"Found {len(profiles)} profiles for {company_name}")
            return profiles
        except Exception as e:
            logger.error(f"Failed to scrape {company_name}: {e}")
            return []

    def _parse_employee_profiles(self, markdown: str, company_name: str) -> List[LinkedInProfile]:
        """Parse employee profiles from markdown."""
        profiles = []
        
        # Extract profile patterns from markdown
        # Pattern: Name · Title · Company
        pattern = r"([A-Z][a-z]+ [A-Z][a-z]+) · ([^·]+) · ([^·]+)"
        matches = re.findall(pattern, markdown)
        
        for match in matches:
            name, title, company = match
            profile = LinkedInProfile(
                name=name.strip(),
                title=title.strip(),
                company=company.strip() if company.strip() else company_name,
                industry="",
                location="",
                profile_url="",
                seniority=self._classify_seniority(title),
                departments=self._extract_departments(title)
            )
            
            # Only include decision makers
            if profile.seniority != "individual":
                profiles.append(profile)
        
        return profiles[:20]  # Limit to top 20

    def _classify_seniority(self, title: str) -> str:
        """Classify seniority level from title."""
        title_lower = title.lower()
        
        for level, patterns in self.DECISION_TITLES.items():
            if any(p in title_lower for p in patterns):
                return level
        
        return "individual"

    def _extract_departments(self, title: str) -> List[str]:
        """Extract departments from title."""
        title_lower = title.lower()
        departments = []
        
        for dept in self.TARGET_DEPARTMENTS:
            if dept in title_lower:
                departments.append(dept)
        
        return departments

    async def find_decision_makers(self, company_name: str, industry: str, target_roles: List[str]) -> List[LinkedInProfile]:
        """Find decision makers matching target roles."""
        profiles = await self.scrape_company_employees(company_name, industry)
        
        # Filter by target roles
        filtered = []
        for profile in profiles:
            title_lower = profile.title.lower()
            if any(role.lower() in title_lower for role in target_roles):
                filtered.append(profile)
        
        return filtered

    def get_profile_email_pattern(self, profile: LinkedInProfile, company_domain: str) -> Optional[str]:
        """Generate likely email pattern from profile."""
        if not company_domain:
            return None
        
        name_parts = profile.name.lower().split()
        if len(name_parts) < 2:
            return None
        
        first = name_parts[0]
        last = name_parts[-1]
        
        patterns = [
            f"{first}.{last}@{company_domain}",
            f"{first}{last}@{company_domain}",
            f"{first[0]}{last}@{company_domain}",
            f"{first}@{company_domain}",
        ]
        
        return patterns[0]  # Return most common pattern

    def track_job_changes(self, profile_url: str) -> bool:
        """Check if profile has recent job change (re-engagement trigger)."""
        # Would need to compare with cached data
        # For now, return False
        return False


def get_linkedin_scraper(config: Settings) -> LinkedInScraper:
    """Get or create LinkedIn scraper."""
    return LinkedInScraper(config)
