"""
Lead Scorer — multi-dimensional priority tiering for outbound leads.

Returns a score dict with total_score, tier (hot/warm/cold/skip), and per-dimension breakdown.
"""

DIMENSIONS = {
    "digital_presence": {"weight": 0.20},
    "social_maturity": {"weight": 0.15},
    "ad_activity": {"weight": 0.15},
    "customer_volume": {"weight": 0.15},
    "response_readiness": {"weight": 0.10},
    "business_size": {"weight": 0.15},
    "match_score": {"weight": 0.10},
}


def _score_digital_presence(lead, research):
    website = (lead.get("websiteUri") or "").strip()
    if not website:
        return 10, "No website — high urgency"
    score = 3
    if research.get("page_speed_slow"):
        score += 2
    if research.get("mobile_friendly") is False:
        score += 2
    if research.get("has_seo") is False:
        score += 2
    detail = "Has website, gaps detected" if score > 3 else "Website looks adequate"
    return min(score, 10), detail


def _score_social_maturity(lead, research):
    social_links = research.get("social_links", [])
    if not social_links:
        if "social_links" in research:
            return 8, "No social media detected"
        return 5, "Social presence unknown"
    score = 3
    if research.get("social_activity") == "active":
        score += 3
    if research.get("social_followers", 0) > 500:
        score += 2
    return min(score, 10), f"{len(social_links)} social accounts found"


def _score_ad_activity(lead, research):
    if research.get("ads_detected"):
        if research.get("ads_quality") == "low":
            return 8, "Running ads but poor quality — optimization opportunity"
        return 4, "Running ads, seems adequate"
    if research.get("competitor_ads_detected"):
        return 7, "Not running ads but competitors are"
    return 5, "No ad activity detected"


def _score_customer_volume(lead, research):
    reviews = 0
    try:
        reviews = int(lead.get("reviewCount") or 0)
    except (ValueError, TypeError):
        pass
    rating = 0
    try:
        rating = float(lead.get("rating") or 0)
    except (ValueError, TypeError):
        pass
    if reviews > 500:
        return 9, f"Very high volume ({reviews} reviews)"
    if reviews > 100:
        return 7, f"High volume ({reviews} reviews)"
    if reviews > 20:
        return 5, f"Moderate volume ({reviews} reviews)"
    return 3, f"Low volume ({reviews} reviews)"


def _score_response_readiness(lead, research):
    website = (lead.get("websiteUri") or "").strip()
    if not website:
        return 3, "No website to assess"
    if research.get("has_livechat"):
        return 2, "Already has live chat"
    return 8, "No live chat detected — opportunity"


def _score_business_size(lead, research):
    vertical = (lead.get("primaryType") or "").lower()
    big_verticals = {"hospital", "hotel", "clinic", "university", "manufacturing"}
    if vertical in big_verticals:
        return 7, f"Large business type ({vertical})"
    employees = research.get("employee_count", 0)
    if employees > 50:
        return 8, "Large business (50+ employees)"
    if employees > 10:
        return 6, "Medium business (10-50 employees)"
    return 4, "Small business"


def _score_match(lead, research):
    from service_detector import detect_services
    try:
        services = detect_services(lead, research)
        if not services:
            return 2, "No strong service match"
        top_score = services[0]["score"]
        if top_score >= 10:
            return 9, f"Excellent match ({services[0]['service']}, score {top_score})"
        if top_score >= 7:
            return 7, f"Good match ({services[0]['service']}, score {top_score})"
        return 4, f"Moderate match (score {top_score})"
    except Exception:
        return 5, "Match unknown"


SCORERS = {
    "digital_presence": _score_digital_presence,
    "social_maturity": _score_social_maturity,
    "ad_activity": _score_ad_activity,
    "customer_volume": _score_customer_volume,
    "response_readiness": _score_response_readiness,
    "business_size": _score_business_size,
    "match_score": _score_match,
}


def score_lead(lead: dict, research: dict) -> dict:
    """Score a lead across 7 dimensions and return tier assignment.

    Args:
        lead: Raw lead dict (e.g. from Google Maps / DB row).
        research: Enrichment dict from researcher/scraper.

    Returns:
        {
            "total_score": float,       # weighted 0-10
            "tier": str,                # hot / warm / cold / skip
            "dimensions": {
                "<dim>": {
                    "score": int,       # 0-10
                    "weight": float,
                    "weighted": float,
                    "detail": str,
                },
                ...
            }
        }
    """
    total = 0.0
    dimensions = {}

    for dim_name, config in DIMENSIONS.items():
        score, detail = SCORERS[dim_name](lead, research)
        weighted = score * config["weight"]
        total += weighted
        dimensions[dim_name] = {
            "score": score,
            "weight": config["weight"],
            "weighted": round(weighted, 2),
            "detail": detail,
        }

    total = round(total, 1)

    if total >= 8:
        tier = "hot"
    elif total >= 5:
        tier = "warm"
    elif total >= 3:
        tier = "cold"
    else:
        tier = "skip"

    return {"total_score": total, "tier": tier, "dimensions": dimensions}
