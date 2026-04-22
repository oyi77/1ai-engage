import sys
from typing import Optional

SERVICE_SIGNALS = {
    "website_development": {
        "priority": 1,
        "signals": {
            "no_website":          {"weight": 10},
            "website_broken":      {"weight": 8},
            "slow_loading":        {"weight": 6},
            "not_mobile_friendly": {"weight": 7},
            "no_seo":              {"weight": 5},
            "no_contact_form":     {"weight": 4},
        },
        "target_verticals": ["restaurant", "cafe", "clinic", "salon", "hotel", "gym", "retail", "digital_agency", "e_commerce", "property", "education"],
    },
    "adforge_ai": {
        "priority": 2,
        "signals": {
            "running_ads_badly":    {"weight": 9},
            "competitor_ads":       {"weight": 7},
            "low_engagement":       {"weight": 5},
            "no_ads_but_competitor": {"weight": 8},
        },
        "target_verticals": ["restaurant", "cafe", "fashion", "beauty_salon", "gym", "real_estate", "digital_agency", "e_commerce"],
    },
    "ai_agent_pro": {
        "priority": 3,
        "signals": {
            "no_chatbot":           {"weight": 8},
            "high_review_count":    {"weight": 6},
            "slow_response":        {"weight": 9},
            "many_locations":       {"weight": 7},
        },
        "target_verticals": ["clinic", "hospital", "restaurant", "hotel", "salon", "gym", "property", "education"],
    },
    "social_media_management": {
        "priority": 4,
        "signals": {
            "no_social_media":      {"weight": 9},
            "inactive_social":      {"weight": 7},
            "low_followers":        {"weight": 5},
            "inconsistent_posting": {"weight": 6},
        },
        "target_verticals": ["restaurant", "cafe", "fashion", "beauty_salon", "hotel", "gym", "entertainment", "retail"],
    },
    "ai_automation": {
        "priority": 5,
        "signals": {
            "manual_booking":       {"weight": 8},
            "paper_based":          {"weight": 7},
            "legacy_tech":          {"weight": 6},
            "many_employees":       {"weight": 5},
        },
        "target_verticals": ["logistics", "manufacturing", "retail", "healthcare", "education", "professional_services"],
    },
}

def _check_signal(signal_name: str, lead: dict, research: dict) -> bool:
    """Check if a specific signal is detected in lead/research data."""
    website = (lead.get("websiteUri") or "").strip()
    reviews = 0
    try:
        reviews = int(lead.get("reviewCount") or 0)
    except (ValueError, TypeError):
        pass
    
    signals = {
        "no_website": not website,
        "website_broken": website and research.get("website_status") == "broken",
        "slow_loading": research.get("page_speed_slow") is True,
        "not_mobile_friendly": research.get("mobile_friendly") is False,
        "no_seo": research.get("has_seo") is False,
        "no_contact_form": research.get("has_contact_form") is False,
        "running_ads_badly": research.get("ads_detected") is True and research.get("ads_quality") == "low",
        "competitor_ads": research.get("competitor_ads_detected") is True,
        "low_engagement": research.get("social_engagement") == "low",
        "no_ads_but_competitor": research.get("competitor_ads_detected") is True and research.get("ads_detected") is not True,
        "no_chatbot": bool(website) and research.get("has_livechat") is not True,
        "high_review_count": reviews > 100,
        "slow_response": research.get("response_time") == "slow",
        "many_locations": research.get("location_count", 0) > 1,
        "no_social_media": "social_links" in research and not research.get("social_links"),
        "inactive_social": research.get("social_activity") == "inactive",
        "low_followers": "social_followers" in research and research.get("social_followers", 0) < 100,
        "inconsistent_posting": research.get("posting_frequency") == "inconsistent",
        "manual_booking": research.get("booking_system") == "manual",
        "paper_based": research.get("paper_based") is True,
        "legacy_tech": research.get("tech_stack_legacy") is True,
        "many_employees": research.get("employee_count", 0) > 10,
    }
    return signals.get(signal_name, False)


def detect_services(lead: dict, research: dict) -> list[dict]:
    """
    Analyze lead + research data to determine which BerkahKarya services to propose.
    Returns list of {"service": str, "score": float, "reasons": list[str]} sorted by score desc.
    Returns top 2 services with score >= 5.0.
    """
    results = []
    vertical = (lead.get("primaryType") or lead.get("type") or "").lower()
    
    for service_name, config in SERVICE_SIGNALS.items():
        score = 0.0
        reasons = []
        for signal_name, signal_config in config["signals"].items():
            if _check_signal(signal_name, lead, research):
                score += signal_config["weight"]
                reasons.append(signal_name)
        
        if vertical in config.get("target_verticals", []):
            score *= 1.3
        
        if score >= 5.0:
            results.append({
                "service": service_name,
                "score": round(score, 1),
                "reasons": reasons,
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:2]
