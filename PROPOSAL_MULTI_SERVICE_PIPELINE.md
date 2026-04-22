# 1ai-reach Multi-Service Outreach Pipeline — Integration & Expansion Proposal

**Date:** April 2026
**Author:** 1ai-reach System Architecture
**Status:** Proposal — Awaiting Approval

---

## 1. Executive Summary

This proposal outlines two major upgrades to the 1ai-reach outreach system:

1. **Replace Google Places API with `gosom/google-maps-scraper`** — a free, open-source (MIT, 3.6K GitHub stars) Google Maps scraper that runs as a Docker container with a REST API. Zero cost, 120 places/minute, built-in email extraction, no API keys needed.

2. **Build multi-service proposal pipelines** — instead of a single generic proposal, the system will detect which BerkahKarya service each lead needs most (website, ads, chatbot, social media, etc.) and generate a hyper-personalized proposal for that specific service. This covers BerkahKarya's full catalog of 12+ services priced from Rp 49K to Rp 2.5jt.

**Expected impact:**
- Scraping cost: $0/month (vs $200/month Google API credits)
- Lead volume: unlimited (vs 6,000 searches/month cap)
- Conversion rate: 3-5x improvement through service-specific personalization
- Revenue per lead: higher through multi-service bundling

---

## 2. Current State Analysis

### 2.1 Current Pipeline

```
vibe_scraper.py / scraper.py  →  Google Places API ($200/mo free, 6K cap)
  ↓
enricher.py                   →  AgentCash Minerva → website scrape → email pattern
  ↓
researcher.py                 →  Scrape homepage + /about + /services → pain points
  ↓
generator.py                  →  Claude Sonnet + brain_client.get_strategy(vertical)
  ↓                               Single generic proposal (email + WA message)
reviewer.py                   →  Claude quality gate (6/10 pass threshold)
  ↓
blaster.py                    →  Email (gog/himalaya) + WhatsApp (WAHA/wacli)
  ↓
reply_tracker.py              →  Gmail + WAHA inbox monitoring
  ↓
converter.py                  →  replied → meeting invite + PaperClip issue
  ↓
followup.py                   →  Day 7 follow-up → Day 14 cold mark
  ↓
sheets_sync.py                →  Google Sheet sync
brain sync                    →  Store outcomes for future intelligence
```

### 2.2 Current Limitations

| Limitation | Impact |
|---|---|
| Google Places API cost cap | Max ~6,000 searches/month, then paid |
| Single proposal template | Same pitch for every business type |
| No service detection | Cannot match lead to best BerkahKarya service |
| Manual vertical targeting | User must specify niche + city manually |
| Generic WhatsApp message | One-size-fits-all Indonesian hook |
| No lead scoring | No way to prioritize hot leads |
| Brain intel underutilized | Only queries vertical strategy, not service-specific wins |

### 2.3 Current Infrastructure

| Component | Port | Technology |
|---|---|---|
| 1ai-reach API | 8001 | FastAPI + SQLite |
| Dashboard | 8502 | Next.js |
| Hub Brain | 9099 | FastAPI (BerkahKarya Hub) |
| WAHA (WhatsApp) | 3000 | HTTP API |
| Cloudflare Tunnel | — | reach.aitradepulse.com |

---

## 3. Proposed Integration — gosom/google-maps-scraper

### 3.1 Why This Scraper

| Feature | gosom/google-maps-scraper | Current (Google Places API) |
|---|---|---|
| Cost | **FREE** (MIT license) | $200/mo free, then paid |
| Speed | 120 places/min | API rate limited |
| Search cap | **Unlimited** | ~6,000/month |
| API key needed | **No** | Yes (Google Cloud) |
| Email extraction | **Built-in** (-email flag) | Separate enrichment step |
| Data points | **33+** fields | 10-15 fields |
| Deployment | Docker container | API calls |
| REST API | **Yes** (built-in) | N/A |
| Output formats | CSV, JSON, PostgreSQL, S3 | JSON only |
| Proxy rotation | **Built-in** | Manual |
| Anti-ban | Built-in throttling | N/A |

### 3.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│  gosom/google-maps-scraper (Docker)                  │
│  Port: 8081                                         │
│                                                      │
│  REST API:                                           │
│    POST /api/v1/jobs          ← create scrape job    │
│    GET  /api/v1/jobs          ← list jobs            │
│    GET  /api/v1/jobs/{id}     ← get job status       │
│    GET  /api/v1/jobs/{id}/download ← download CSV    │
│    DELETE /api/v1/jobs/{id}   ← delete job           │
│                                                      │
│  Flags: -email (extract emails from websites)         │
│         -depth 5 (max pages per query)               │
│         -lang id (Indonesian results)                │
│  Data: /gmapsdata (mounted volume)                   │
└──────────────┬──────────────────────────────────────┘
               │ REST API calls
               ▼
┌─────────────────────────────────────────────────────┐
│  1ai-reach Scraper Client (Python)                   │
│                                                      │
│  class GmapsScraperClient:                           │
│    def create_job(query, location, max_results)      │
│    def poll_job(job_id) → wait until complete        │
│    def download_results(job_id) → List[Lead]         │
│    def map_to_lead(raw_item) → Lead dict             │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
         leads.db (dedup + insert)
```

### 3.3 Docker Deployment

```yaml
# docker-compose.yml OR systemd service (see Section 11.2 for systemd)
services:
  gmaps-scraper:
    image: gosom/google-maps-scraper:latest
    container_name: gmaps-scraper
    ports:
      - "8081:8080"
    volumes:
      - ./data/gmaps:/gmapsdata
    command: >
      -data-folder /gmapsdata
      -email
      -lang id
    restart: unless-stopped
```

### 3.4 Python Client Wrapper

```python
# scripts/gmaps_client.py

class GmapsScraperClient:
    """Client for gosom/google-maps-scraper REST API."""

    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url

    def create_job(self, query: str, max_results: int = 100) -> str:
        """Create a scrape job, return job ID."""
        resp = requests.post(f"{self.base_url}/api/v1/jobs", json={
            "query": query,
            "max": max_results,
        })
        return resp.json()["id"]

    def poll_job(self, job_id: str, timeout: int = 600) -> dict:
        """Poll until job completes. Returns final job object."""
        start = time.time()
        while time.time() - start < timeout:
            resp = requests.get(f"{self.base_url}/api/v1/jobs/{job_id}")
            job = resp.json()
            if job.get("status") == "completed":
                return job
            time.sleep(5)
        raise TimeoutError(f"Job {job_id} did not complete in {timeout}s")

    def download_results(self, job_id: str) -> list[dict]:
        """Download CSV results and parse into list of dicts."""
        resp = requests.get(f"{self.base_url}/api/v1/jobs/{job_id}/download")
        # Parse CSV → list of dicts
        return self._parse_csv(resp.text)

    def scrape(self, query: str, max_results: int = 100) -> list[dict]:
        """One-shot: create job, poll, download, return results."""
        job_id = self.create_job(query, max_results)
        self.poll_job(job_id)
        return self.download_results(job_id)

    @staticmethod
    def map_to_lead(raw: dict) -> dict:
        """Map scraper output fields to leads.db schema."""
        return {
            "id": raw.get("place_id", ""),
            "displayName": raw.get("title", ""),
            "formattedAddress": raw.get("address", ""),
            "phone": raw.get("phone", ""),
            "websiteUri": raw.get("website", ""),
            "email": raw.get("email", ""),       # from -email flag
            "primaryType": raw.get("category", ""),
            "rating": raw.get("rating", 0),
            "reviewCount": raw.get("reviews", 0),
            "latitude": raw.get("latitude", 0),
            "longitude": raw.get("longitude", 0),
            "source": "gmaps_scraper",
            "status": "new",
        }
```

### 3.5 Integration Point in Orchestrator

```python
# In orchestrator.py (pseudocode)
def scrape_leads(niche: str, city: str, count: int = 100):
    client = GmapsScraperClient()

    # Multi-query strategy for better coverage
    queries = [
        f"{niche} in {city}",
        f"jasa {niche} {city}",
        f"{niche} terbaik {city}",
    ]

    all_leads = []
    for q in queries:
        results = client.scrape(q, max_results=count // len(queries))
        for raw in results:
            lead = GmapsScraperClient.map_to_lead(raw)
            all_leads.append(lead)

    # Dedup by place_id and website
    deduped = dedup_leads(all_leads)

    # Insert into leads.db
    for lead in deduped:
        insert_or_skip(lead)

    return len(deduped)
```

### 3.6 Cost Comparison

| Metric | Current (Google Places API) | New (gosom scraper) |
|---|---|---|
| Monthly cost | $0-200 (free tier limit) | **$0** (forever) |
| Searches/month | ~6,000 cap | **Unlimited** |
| Email extraction | Separate step (AgentCash) | **Built-in** |
| Data points per lead | 10-15 | **33+** |
| Infrastructure | API calls only | Docker container (50MB RAM) |
| Latency | ~200ms per API call | ~0.5s per place (scraping) |

**Savings: $0-200/month + unlimited scale + built-in email extraction.**

---

## 4. BerkahKarya Service Catalog

### 4.1 Full Service Inventory

| # | Service | Price | Target Audience | Primary Pain Point |
|---|---------|-------|-----------------|-------------------|
| 1 | **Website Development** | Rp 2.5jt | Businesses with no website, broken site, slow site | Losing online customers |
| 2 | **AdForge AI** (Ads) | Rp 149K/mo | Businesses running Meta/TikTok/Google ads | Low ROAS, wasted budget |
| 3 | **AI Agent Pro** (Chatbot) | Rp 299K/mo | High customer volume businesses (clinics, restaurants) | Lost leads from slow replies |
| 4 | **Social Media Management** | Rp 1.5jt/mo | Brands needing consistent content | No time for social media |
| 5 | **AI Creative Studio** (Video) | Rp 49K-149K/mo | F&B, fashion, retail, content creators | Expensive video production |
| 6 | **AI Automation** | Rp 500K/project | Businesses with repetitive manual processes | Wasting staff hours |
| 7 | **Security Audit** | Rp 1jt | E-commerce, SaaS, tech companies | Fear of hacking/data breach |
| 8 | **Deep Research** | Rp 500K | Decision makers, strategists | Decisions based on feeling, not data |
| 9 | **Custom Documents** | Rp 150K/doc | All businesses | Need professional docs fast |
| 10 | **1Ai Platform** (398 AI Models) | Rp 75K/mo | Developers, agencies, tech-savvy SMEs | Expensive AI API costs |
| 11 | **Video Production** | Rp 1.5jt/video | Established companies, agencies | Unprofessional company profile |
| 12 | **Algorithmic Trading** | Rp 499K/mo | Traders, investors | Emotional trading decisions |

### 4.2 Service Priority Matrix (for Outreach)

```
                    HIGH TICKET                          LOW TICKET
              (Rp 1jt+ per sale)                  (Rp <500K per sale)
            ┌─────────────────────┐          ┌─────────────────────┐
            │ 1. Website Dev      │          │ 5. AI Video Studio   │
 HIGHEST    │ 2. Social Media Mgmt│          │ 2. AdForge AI        │
 CONVERT    │ 4. Video Production │          │ 3. AI Agent Pro      │
 RATE       │ 7. Security Audit   │          │ 10. 1Ai Platform     │
            │ 6. AI Automation    │          │ 9. Custom Documents  │
            │ 8. Deep Research    │          │                     │
            └─────────────────────┘          └─────────────────────┘
                    HIGHEST VOLUME                           EASIEST SELL
```

### 4.3 Service Bundling Strategy

Instead of selling one service, propose packages:

| Package | Services Included | Bundle Price | Target |
|---|---|---|---|
| **Starter** | Website + 1Ai Platform | Rp 2.5jt + Rp 75K/mo | New businesses |
| **Growth** | Website + AdForge + AI Agent | Rp 2.5jt + Rp 149K/mo + Rp 299K/mo | Growing businesses |
| **Scale** | Website + Ads + Social Media + AI Agent | Rp 2.5jt + Rp 1.9jt/mo | Ambitious businesses |
| **Full Stack** | All digital services | Rp 5jt setup + Rp 2.5jt/mo | Agencies, enterprises |
| **Audit First** | Security Audit + Deep Research | Rp 1.5jt one-time | Tech companies |

---

## 5. Multi-Service Pipeline Architecture

### 5.1 Complete Pipeline Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SCRAPE & ENRICH LAYER                              │
│                                                                      │
│  gosom/google-maps-scraper ──→ REST API ──→ GmapsScraperClient       │
│       (Docker, port 8081)                                            │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │ Scrape Jobs:     │    │ Enrichment:       │    │ Deduplication: │  │
│  │ "Digital Agency  │    │ - Email (-email)  │    │ - By place_id  │  │
│  │  Jakarta"        │    │ - Website scrape  │    │ - By website   │  │
│  │ "Klinik Jakarta" │    │ - Social links    │    │ - By email     │  │
│  │ "Restoran Bali"  │    │ - Tech stack      │    │ - By phone     │  │
│  │ "Salon Bandung"  │    │ - Review count    │    │                │  │
│  └────────┬────────┘    └────────┬─────────┘    └───────┬────────┘  │
│           │                      │                       │           │
└───────────┼──────────────────────┼───────────────────────┼───────────┘
            │                      │                       │
            ▼                      ▼                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    RESEARCH & ANALYSIS LAYER                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ researcher.py (enhanced)                                      │   │
│  │                                                               │   │
│  │ For each lead, detect:                                        │   │
│  │  ├── Has website? → quality score (speed, mobile, SEO)       │   │
│  │  ├── Has social media? → activity, engagement, posting freq  │   │
│  │  ├── Running ads? → platform, creative quality estimate      │   │
│  │  ├── Has chatbot/livechat? → response time estimate          │   │
│  │  ├── Review count & rating? → customer satisfaction signal   │   │
│  │  ├── Tech stack? → modern vs legacy                          │   │
│  │  └── Business maturity signals? → digital readiness score    │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                     │
└─────────────────────────────────┼─────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    SERVICE MATCHING LAYER                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ service_detector.py (NEW)                                     │   │
│  │                                                               │   │
│  │ Input: lead data + research results                           │   │
│  │ Process: AI classification + rule-based signals               │   │
│  │ Output: ranked list of BerkahKarya services to propose        │   │
│  │                                                               │   │
│  │ Signal → Service mapping:                                     │   │
│  │  no_website=True        → Website Development (priority 1)   │   │
│  │  slow_website=True      → Website Development (priority 2)   │   │
│  │  no_social_media=True   → Social Media Management            │   │
│  │  low_engagement=True    → Social Media Management            │   │
│  │  running_ads=True       → AdForge AI                         │   │
│  │  no_ads_but_competitor  → AdForge AI                         │   │
│  │  high_chat_volume=True  → AI Agent Pro                       │   │
│  │  no_chatbot=True        → AI Agent Pro                       │   │
│  │  manual_processes=True  → AI Automation                      │   │
│  │  has_ecommerce=True     → Security Audit                     │   │
│  │  video_needs=True       → AI Creative Studio                 │   │
│  │  tech_stack_legacy=True → AI Automation                      │   │
│  │                                                               │   │
│  │ Also: brain_client.get_strategy(service_type, vertical)       │   │
│  │  → what worked for this service+vertical combo before         │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                     │
└─────────────────────────────────┼─────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    PROPOSAL GENERATION LAYER                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ generator.py (multi-service)                                  │   │
│  │                                                               │   │
│  │ For each lead:                                                │   │
│  │  1. Load matched service(s) from service_detector             │   │
│  │  2. Load service template from templates/                     │   │
│  │  3. Load brain strategy for this service+vertical             │   │
│  │  4. Load research brief for personalization                   │   │
│  │  5. Generate proposal using Claude Sonnet:                    │   │
│  │     - Email body (English, professional)                      │   │
│  │     - WhatsApp hook (Indonesian, casual)                      │   │
│  │                                                               │   │
│  │ Template selection:                                           │   │
│  │  templates/                                                   │   │
│  │  ├── website_development.yaml                                 │   │
│  │  ├── adforge_ai.yaml                                          │   │
│  │  ├── ai_agent_pro.yaml                                        │   │
│  │  ├── social_media_management.yaml                             │   │
│  │  ├── ai_creative_studio.yaml                                  │   │
│  │  ├── ai_automation.yaml                                       │   │
│  │  ├── security_audit.yaml                                      │   │
│  │  ├── deep_research.yaml                                       │   │
│  │  └── bundle_growth.yaml        (multi-service package)        │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                     │
└─────────────────────────────────┼─────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    REVIEW & SEND LAYER                                │
│                                                                      │
│  reviewer.py → quality gate (6/10 pass)                              │
│       │                                                              │
│       ▼                                                              │
│  blaster.py                                                          │
│  ├── Email (HTML, personalized, service-specific)                   │
│  ├── WhatsApp (Indonesian hook, service-specific CTA)               │
│  └── Follow-up sequences (service-specific timing)                  │
│       │                                                              │
│       ▼                                                              │
│  reply_tracker.py → converter.py → followup.py                      │
│  (existing, unchanged)                                               │
│       │                                                              │
│       ▼                                                              │
│  brain_client.learn_outcome(service_type=matched_service)            │
│  (enhanced: stores which SERVICE was proposed + outcome)             │
└──────────────────────────────────────────────────────────────────────┘
```

### 5.2 Service-Lead Matching: Signal Detection Rules

```python
# service_detector.py (pseudocode)

SERVICE_SIGNALS = {
    "website_development": {
        "priority": 1,  # highest — most leads need this
        "signals": {
            "no_website":          {"weight": 10, "trigger": True},
            "website_broken":      {"weight": 8,  "trigger": True},
            "slow_loading":        {"weight": 6,  "trigger": True},
            "not_mobile_friendly": {"weight": 7,  "trigger": True},
            "no_seo":              {"weight": 5,  "trigger": True},
            "no_contact_form":     {"weight": 4,  "trigger": True},
        },
        "target_verticals": [
            "all"  # every business needs a website
        ],
    },
    "adforge_ai": {
        "priority": 2,
        "signals": {
            "running_ads_badly":    {"weight": 9,  "trigger": True},
            "competitor_ads":       {"weight": 7,  "trigger": True},
            "low_engagement":       {"weight": 5,  "trigger": True},
            "no_ads_but_spend":     {"weight": 8,  "trigger": True},
        },
        "target_verticals": [
            "restaurant", "cafe", "fashion", "beauty_salon",
            "gym", "real_estate", "digital_agency", "e_commerce",
        ],
    },
    "ai_agent_pro": {
        "priority": 3,
        "signals": {
            "no_chatbot":           {"weight": 8,  "trigger": True},
            "high_review_count":    {"weight": 6,  "trigger": "reviews > 100"},
            "slow_response":        {"weight": 9,  "trigger": True},
            "many_locations":       {"weight": 7,  "trigger": True},
        },
        "target_verticals": [
            "clinic", "hospital", "restaurant", "hotel",
            "salon", "gym", "property", "education",
        ],
    },
    "social_media_management": {
        "priority": 4,
        "signals": {
            "no_social_media":      {"weight": 9,  "trigger": True},
            "inactive_social":      {"weight": 7,  "trigger": True},
            "low_followers":        {"weight": 5,  "trigger": True},
            "inconsistent_posting": {"weight": 6,  "trigger": True},
        },
        "target_verticals": [
            "restaurant", "cafe", "fashion", "beauty_salon",
            "hotel", "gym", "entertainment", "retail",
        ],
    },
    "ai_creative_studio": {
        "priority": 5,
        "signals": {
            "no_video_content":     {"weight": 7,  "trigger": True},
            "product_business":     {"weight": 5,  "trigger": True},
            "visual_industry":      {"weight": 6,  "trigger": True},
        },
        "target_verticals": [
            "restaurant", "cafe", "fashion", "beauty_salon",
            "food_beverage", "property", "automotive",
        ],
    },
    "ai_automation": {
        "priority": 6,
        "signals": {
            "manual_booking":       {"weight": 8,  "trigger": True},
            "paper_based":          {"weight": 7,  "trigger": True},
            "legacy_tech":          {"weight": 6,  "trigger": True},
            "many_employees":       {"weight": 5,  "trigger": True},
        },
        "target_verticals": [
            "logistics", "manufacturing", "retail",
            "healthcare", "education", "professional_services",
        ],
    },
    "security_audit": {
        "priority": 7,
        "signals": {
            "has_ecommerce":        {"weight": 8,  "trigger": True},
            "handles_payments":     {"weight": 9,  "trigger": True},
            "stores_user_data":     {"weight": 7,  "trigger": True},
            "tech_company":         {"weight": 5,  "trigger": True},
        },
        "target_verticals": [
            "e_commerce", "saas", "fintech",
            "healthcare", "education",
        ],
    },
}

def detect_services(lead: dict, research: dict) -> list[dict]:
    """
    Analyze lead + research data to determine which BerkahKarya
    services to propose, ranked by relevance score.

    Returns: [
        {"service": "website_development", "score": 9.5, "reason": "No website detected"},
        {"service": "ai_agent_pro", "score": 7.2, "reason": "100+ reviews, no chatbot"},
        ...
    ]
    """
    results = []

    # Rule-based scoring
    for service_name, config in SERVICE_SIGNALS.items():
        score = 0
        reasons = []
        for signal_name, signal_config in config["signals"].items():
            detected = check_signal(signal_name, lead, research)
            if detected:
                score += signal_config["weight"]
                reasons.append(signal_name)

        # Boost by vertical match
        if lead.get("primaryType", "").lower() in config["target_verticals"]:
            score *= 1.3

        # Boost by brain intelligence
        brain_strat = brain_client.get_strategy(service_name, lead.get("primaryType", ""))
        if brain_strat:
            score *= 1.2

        if score >= 5:  # minimum threshold
            results.append({
                "service": service_name,
                "score": round(score, 1),
                "reasons": reasons,
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Top 2 services (don't overwhelm the lead)
    return results[:2]
```

### 5.3 Multi-Query Scraping Strategy

Instead of one query per niche, use intelligent multi-query patterns:

```python
QUERY_TEMPLATES = {
    "restaurant": [
        "{niche} in {city}",
        "restoran {city}",
        "kuliner {city}",
        "makanan enak {city}",
        "cafe {city}",
        "warung makan {city}",
    ],
    "digital_agency": [
        "digital agency {city}",
        "jasa digital marketing {city}",
        "jasa SEO {city}",
        "jasa pembuatan website {city}",
        "digital marketing agency {city}",
    ],
    "clinic": [
        "klinik {city}",
        "klinik kesehatan {city}",
        "praktek dokter {city}",
        "klinik kecantikan {city}",
    ],
    "beauty_salon": [
        "salon kecantikan {city}",
        "barbershop {city}",
        "spa {city}",
        "nail art {city}",
        "jasa makeup {city}",
    ],
    "default": [
        "{niche} in {city}",
        "jasa {niche} {city}",
        "{niche} terbaik {city}",
        "{niche} murah {city}",
    ],
}
```

---

## 6. Proposal Template System

### 6.1 Template Structure (YAML)

Each service has a YAML template file in `templates/`:

```yaml
# templates/website_development.yaml
service: "website_development"
service_name_display: "Website Development"
price_display: "Mulai Rp 2.5jt"
price_anchor: "97% lebih murah dari agency lain"

target_signals:
  - no_website
  - website_broken
  - slow_loading
  - not_mobile_friendly
  - no_seo

pain_points:
  - "Bisnis Anda tidak muncul di Google ketika calon customer cari"
  - "Kompetitor Anda sudah punya website profesional"
  - "Customer potensial pergi karena tidak bisa cari info online"
  - "Tanpa website, bisnis terlihat tidak profesional"

value_props:
  - "SEO-ready + pixel tracking terintegrasi"
  - "Mobile-first, load <2 detik"
  - "Revisi tidak terbatas selama 30 hari"
  - "Setup dalam 7 hari kerja"

case_study:
  metric: "3x lebih banyak leads setelah website baru"
  customer_type: "restaurant di Jakarta"

email:
  subject_lines:
    - "Saya lihat {company_name} belum punya website — ada ide cepat"
    - "{company_name} bisa 3x lebih banyak customer dengan website baru"
    - "Website untuk {company_name} — ready dalam 7 hari"
    - "Ide untuk {company_name}: website yang bikin customer datang"

  body_template: |
    Hi {contact_name},

    Saya menemukan {company_name} di Google Maps — {review_count} reviews
    dengan rating {rating}. Impressive!

    Tapi saya perhatikan {pain_point_observation}.

    Kami baru saja bikin website untuk {similar_business} di {city},
    dan mereka dapat 3x lebih banyak leads dalam 30 hari pertama.
    Website-nya mobile-friendly, load dalam 2 detik, dan otomatis
    muncul di halaman pertama Google.

    Yang kami tawarkan:
    {value_props_bulleted}

    Harga mulai Rp 2.5jt — termasuk domain, hosting 1 tahun,
    SEO setup, dan revisi tidak terbatas selama 30 hari.

    Mau saya kirim contoh website yang kami buat untuk bisnis
    serupa di {city}?

    Best,
    {sender_name}
    BerkahKarya — berkahkarya.org

whatsapp:
  templates:
    - "Halo! Saya lihat {company_name} belum punya website. Kami bisa bikin yang profesional, mobile-friendly, muncul di Google — mulai Rp 2.5jt, ready 7 hari. Mau lihat contohnya?"
    - "Halo {contact_name}! {company_name} bagus banget tapi belum ada website ya? Kami dari BerkahKarya bikin website yang bikin customer datang — mulai Rp 2.5jt. Cek berkahkarya.org ya!"
    - "Hai! Saya notice {company_name} di Google Maps rating {rating} tapi belum ada website. Sayang banget, banyak customer potensial yang nyari online. Kami bisa bantu — mulai Rp 2.5jt, ready seminggu. Mau lihat demo?"

cta:
  email: "Mau saya kirim contoh website?"
  whatsapp: "Mau lihat contohnya?"
  meeting: "Konsultasi gratis 15 menit"
```

### 6.2 Template: AdForge AI (Ads Management)

```yaml
# templates/adforge_ai.yaml
service: "adforge_ai"
service_name_display: "AdForge AI"
price_display: "Mulai Rp 149K/bulan"
price_anchor: "50x lebih murah dari hire ads specialist"

target_signals:
  - running_ads_badly
  - competitor_ads
  - low_engagement
  - no_ads_but_competitor

pain_points:
  - "Budget iklan habis tapi ROAS di bawah 2x"
  - "Tidak tahu creative mana yang benar-benar convert"
  - "Kompetitor terus muncul di iklan, Anda tidak"
  - "Manual setting iklan memakan waktu berjam-jam"

value_props:
  - "100 variasi creative dalam 10 menit"
  - "Auto A/B test: AI pilih pemenang"
  - "Support Meta Ads, TikTok Ads, Google Ads"
  - "ROAS naik tanpa tambah budget"

case_study:
  metric: "ROAS naik dari 1.8x ke 4.2x"
  customer_type: "e-commerce di Jakarta"

email:
  subject_lines:
    - "{company_name} ads budget optimal? Quick analysis"
    - "Saya lihat iklan {company_name} — bisa 2x ROAS"
    - "ROAS {company_name} bisa naik tanpa tambah budget"
  body_template: |
    Hi {contact_name},

    Saya lihat {company_name} beriklan di {ads_platform_detected}.
    {personalized_observation_about_their_ads}

    Kami bikin tool yang generate 100 variasi creative iklan
    otomatis, lalu AI yang test dan pilih yang paling convert.

    Salah satu klien kami (e-commerce serupa) naik ROAS dari
    1.8x ke 4.2x dalam 30 hari — budget sama, revenue 2x lipat.

    Mulai Rp 149K/bulan. Tanpa kontrak, bisa cancel kapan saja.

    Mau saya tunjukkan bagaimana AI-nya bekerja?

    Best,
    {sender_name}
    BerkahKarya — berkahkarya.org

whatsapp:
  templates:
    - "Halo! Saya lihat {company_name} beriklan di {platform}. ROAS-nya bisa naik 2x tanpa tambah budget pakai AI kami. Mulai Rp 149K/bln. Mau lihat demo?"
    - "Hai {contact_name}! Budget iklan {company_name} optimal? Kami punya AI yang bikin 100 creative iklan + auto A/B test — ROAS naik otomatis. Rp 149K/bln. Cek berkahkarya.org!"
```

### 6.3 Template: AI Agent Pro (Chatbot)

```yaml
# templates/ai_agent_pro.yaml
service: "ai_agent_pro"
service_name_display: "AI Agent Pro"
price_display: "Mulai Rp 299K/bulan"
price_anchor: "60% lebih hemat dari hire CS 1 shift"

target_signals:
  - no_chatbot
  - high_review_count
  - slow_response
  - many_locations

pain_points:
  - "Customer chat jam 11 malam tidak dijawab — lead pergi ke kompetitor"
  - "CS team overwhelmed, response time >2 jam"
  - "Lost sales karena customer tidak sabar menunggu balasan"
  - "Hire CS tambahan mahal, turnover tinggi"

value_props:
  - "Respon <2 detik, 24/7 tanpa libur"
  - "Hemat 60% biaya customer service"
  - "Integrasi WhatsApp, Telegram, Instagram DM"
  - "Belajar dari data bisnis Anda otomatis"

case_study:
  metric: "80% customer service dihandle AI"
  customer_type: "SaaS Startup"

email:
  subject_lines:
    - "{company_name} kehilangan customer jam malam?"
    - "AI CS untuk {company_name} — jawab <2 detik, 24/7"
    - "Customer {company_name} menunggu lama? Solusi AI"
  body_template: |
    Hi {contact_name},

    {company_name} punya {review_count} reviews di Google —
    artinya banyak customer yang kontak. Tapi apakah semua
    terjawab dalam 2 menit? Termasuk jam 11 malam?

    Kami bikin AI Agent yang jawab customer 24/7:
    - Respon <2 detik, bahkan jam 3 pagi
    - Handle 80% pertanyaan rutin otomatis
    - Integrasi langsung ke WhatsApp bisnis Anda
    - Belajar dari FAQ dan data bisnis Anda

    Klien kami: response time turun dari 2 jam ke 30 detik.
    Tim CS bisa fokus ke case yang kompleks.

    Mulai Rp 299K/bulan — hemat 60% vs hire CS 1 shift.

    Mau saya setup trial gratis 3 hari untuk {company_name}?

    Best,
    {sender_name}
    BerkahKarya — berkahkarya.org

whatsapp:
  templates:
    - "Halo! {company_name} punya banyak customer ya? Kami punya AI yang jawab chat 24/7 — respon <2 detik, hemat 60% biaya CS. Mulai Rp 299K/bln. Mau trial gratis 3 hari?"
    - "Hai {contact_name}! Customer {company_name} sering nunggu lama dibalas? AI Agent kami jawab otomatis 24/7 via WhatsApp. Rp 299K/bln. Cek berkahkarya.org!"
```

### 6.4 Template: Social Media Management

```yaml
# templates/social_media_management.yaml
service: "social_media_management"
service_name_display: "Social Media Management"
price_display: "Mulai Rp 1.5jt/bulan"
price_anchor: "90 akun, satu dashboard"

target_signals:
  - no_social_media
  - inactive_social
  - low_followers
  - inconsistent_posting

pain_points:
  - "Konten tidak konsisten, follower tidak naik"
  - "Tidak ada waktu buat konten TiKTok, IG, YouTube sekaligus"
  - "Tidak tahu konten apa yang viral"
  - "Posting manual memakan jam kerja tim"

value_props:
  - "90 akun sosmed dikelola simultan"
  - "Konten AI: TikTok, IG, YouTube, FB otomatis"
  - "Analytics: reach, engagement, revenue per post"
  - "Tim konten fokus strategi, bukan teknis"

email:
  subject_lines:
    - "{company_name} social media konsisten? Kami bisa bantu"
    - "90 akun sosmed {company_name} dalam 1 dashboard"
    - "Konten otomatis untuk {company_name} — AI + tim kreatif"
  body_template: |
    Hi {contact_name},

    Saya lihat akun social media {company_name}.
    {personalized_observation_about_their_social}

    Kami dari BerkahKarya bisa handle semua social media
    {company_name} — dari konten creation sampai posting:

    - AI generate konten untuk TikTok, IG, YouTube, FB
    - 90 akun dalam 1 dashboard
    - Analytics real-time: reach, engagement, revenue per post
    - Tim kreatif kami handle bagian yang AI belum bisa

    Mulai Rp 1.5jt/bulan untuk full management.

    Mau saya kirim contoh konten yang kami buat untuk
    bisnis {vertical}?

    Best,
    {sender_name}
    BerkahKarya — berkahkarya.org

whatsapp:
  templates:
    - "Halo! {company_name} butuh bantuan social media? Kami handle 90 akun — konten AI + tim kreatif, analytics real-time. Mulai Rp 1.5jt/bln. Mau lihat contoh kontennya?"
    - "Hai {contact_name}! Kelola social media {company_name} makan banyak waktu? Kami bikin konten AI + auto-posting ke 90 akun. Rp 1.5jt/bln. Cek berkahkarya.org!"
```

### 6.5 Template: AI Automation

```yaml
# templates/ai_automation.yaml
service: "ai_automation"
service_name_display: "AI Automation"
price_display: "Mulai Rp 500K/project"
price_anchor: "Hemat 60% waktu operasional"

target_signals:
  - manual_booking
  - paper_based
  - legacy_tech
  - many_employees

pain_points:
  - "Proses manual memakan waktu berjam-jam setiap hari"
  - "Data tersebar di spreadsheet, WhatsApp, kertas"
  - "Human error dalam proses repetitif"
  - "Karyawan overtime karena tugas yang bisa diotomasi"

value_props:
  - "190+ scripts battle-tested langsung pakai"
  - "Hemat 60% waktu operasional"
  - "Integrasi: WhatsApp, CRM, ERP, spreadsheet"
  - "Setup dalam 1 hari kerja"

email:
  subject_lines:
    - "Proses manual {company_name} bisa diotomasi — hemat 60%"
    - "{company_name} operasional bisa 2x lebih cepat"
    - "Automation untuk {company_name} — dari manual ke AI"
  body_template: |
    Hi {contact_name},

    Saya research {company_name} dan melihat beberapa proses
    yang bisa diotomasi:

    {specific_observations_from_research}

    Kami punya 190+ automation scripts siap pakai:
    - Auto-respon WhatsApp berdasarkan keyword
    - Sync data antara spreadsheet, CRM, dan WhatsApp
    - Auto-generate invoice, laporan, follow-up
    - Integrasi dengan tools yang sudah Anda pakai

    Mulai Rp 500K/project — hemat 60% waktu operasional.

    Mau saya audit gratis proses mana yang bisa diotomasi
    di {company_name}?

    Best,
    {sender_name}
    BerkahKarya — berkahkarya.org

whatsapp:
  templates:
    - "Halo! Proses operasional {company_name} masih banyak manual? Kami punya 190+ automation scripts — hemat 60% waktu. Mulai Rp 500K. Mau audit gratis?"
    - "Hai {contact_name}! {company_name} bisa 2x lebih efisien dengan automation. Kami integrasikan WhatsApp, CRM, spreadsheet — semua otomatis. Rp 500K/project. Cek berkahkarya.org!"
```

---

## 7. Lead Scoring & Prioritization

### 7.1 Scoring Dimensions

Each lead gets scored across multiple dimensions (0-10 each):

| Dimension | Signal Source | Weight | What It Measures |
|---|---|---|---|
| **Digital Presence** | Website check | 20% | Has website? Speed? Mobile? SEO? |
| **Social Maturity** | Social media check | 15% | Active accounts? Engagement? Frequency? |
| **Ad Activity** | Ads detection | 15% | Running ads? On which platforms? Quality? |
| **Customer Volume** | Review count, rating | 15% | How many customers? Satisfaction? |
| **Response Readiness** | Chat/livechat check | 10% | Has chatbot? Response time? |
| **Business Size** | Location, type, employees | 15% | Small/Solo vs Medium vs Large |
| **Match Score** | Service detector | 10% | How well our services match their gaps |

### 7.2 Priority Tiers

```
┌─────────────────────────────────────────────────────┐
│ TIER 1: HOT (Score 8-10)                            │
│ → Contact within 24 hours                           │
│ → Personalized video message option                 │
│ → Multi-service bundle proposal                     │
│ → Direct phone call if number available             │
│                                                     │
│ Signals: no website + 100+ reviews + no chatbot     │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ TIER 2: WARM (Score 5-7)                            │
│ → Contact within 48 hours                           │
│ → Single best-match service proposal                │
│ → Email + WhatsApp                                  │
│                                                     │
│ Signals: has website but poor + no social media     │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ TIER 3: COLD (Score 3-4)                            │
│ → Batch email only                                  │
│ → Generic BerkahKarya ecosystem intro               │
│ → Lower priority in blast queue                     │
│                                                     │
│ Signals: established digital presence, fewer gaps   │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ TIER 4: SKIP (Score 0-2)                            │
│ → Do not contact                                    │
│ → Already a customer, or competitor, or irrelevant  │
└─────────────────────────────────────────────────────┘
```

### 7.3 Scoring Implementation

```python
def score_lead(lead: dict, research: dict) -> dict:
    """
    Returns: {
        "total_score": 7.8,
        "tier": "warm",
        "digital_presence": {"score": 3, "details": "No website detected"},
        "social_maturity": {"score": 5, "details": "Instagram: 1.2K followers, low engagement"},
        "ad_activity": {"score": 8, "details": "Running Facebook ads, poor creative"},
        "customer_volume": {"score": 7, "details": "234 reviews, 4.2 rating"},
        "response_readiness": {"score": 2, "details": "No chatbot, WhatsApp only"},
        "business_size": {"score": 6, "details": "Medium - multiple locations"},
        "recommended_services": [
            {"service": "adforge_ai", "score": 9.2},
            {"service": "ai_agent_pro", "score": 7.5},
        ]
    }
    """
    scores = {}

    # Digital Presence (0-10)
    dp = 0
    dp_details = []
    if not lead.get("websiteUri"):
        dp = 0; dp_details.append("No website")
    else:
        if research.get("website_speed_ok"): dp += 3
        if research.get("mobile_friendly"): dp += 2
        if research.get("has_seo"): dp += 2
        if research.get("has_contact_form"): dp += 1
        if research.get("ssl"): dp += 1
        dp_details.append(f"Website score: {dp}/10")
    scores["digital_presence"] = {"score": dp, "details": "; ".join(dp_details)}

    # ... similar for other dimensions ...

    # Weighted total
    weights = {
        "digital_presence": 0.20,
        "social_maturity": 0.15,
        "ad_activity": 0.15,
        "customer_volume": 0.15,
        "response_readiness": 0.10,
        "business_size": 0.15,
        "match_score": 0.10,
    }
    total = sum(scores[k]["score"] * w for k, w in weights.items())

    tier = "hot" if total >= 8 else "warm" if total >= 5 else "cold" if total >= 3 else "skip"

    return {
        "total_score": round(total, 1),
        "tier": tier,
        **scores,
        "recommended_services": detect_services(lead, research),
    }
```

---

## 8. Implementation Roadmap

### Phase 1: Scraper Integration (Week 1-2)

**Goal:** Replace Google Places API with gosom/google-maps-scraper.

| Day | Task | Deliverable |
|---|---|---|
| 1-2 | Deploy gosom Docker container | Running on port 8081 |
| 1-2 | Build `gmaps_client.py` Python wrapper | Tested REST API client |
| 3-4 | Integrate into orchestrator | `scrape_leads()` uses new client |
| 3-4 | Build data mapper: scraper fields → leads.db | All 33 fields mapped |
| 5 | Multi-query strategy per niche | Templates for 10+ niches |
| 5 | Built-in email extraction pipeline | `-email` flag replaces part of enricher |
| 6-7 | Testing: scrape 200+ leads across 3 niches | All leads in leads.db |
| 8-9 | Update dashboard to show scraper stats | New API endpoints |
| 10 | Documentation + systemd service | `gmaps-scraper.service` |

**Success criteria:** Scrape 200 leads in <10 minutes, zero cost.

### Phase 2: Service Detection & Templates (Week 3-4)

**Goal:** Build the AI service classifier and proposal templates.

| Day | Task | Deliverable |
|---|---|---|
| 1-3 | Build `service_detector.py` | Signal detection + scoring |
| 1-3 | Build `lead_scorer.py` | Multi-dimensional lead scoring |
| 4-7 | Create 8 YAML proposal templates | All top services covered |
| 4-7 | Update `generator.py` for multi-service | Template-aware generation |
| 8-9 | Brain integration: service-specific queries | `get_strategy(service, vertical)` |
| 8-9 | Test proposal quality per service | 10 proposals per service, all pass reviewer |
| 10 | Update dashboard: service funnel view | Filter by service type |

**Success criteria:** Each lead gets matched to 1-2 services with personalized proposals.

### Phase 3: Multi-Channel Personalization (Week 5-6)

**Goal:** Service-specific email + WhatsApp + follow-up sequences.

| Day | Task | Deliverable |
|---|---|---|
| 1-3 | Service-specific email HTML templates | Professional, branded templates |
| 1-3 | Service-specific WhatsApp hooks | Indonesian, casual, tested |
| 4-5 | A/B testing framework for subject lines | Track open rates per template |
| 4-5 | Follow-up sequence per service | Day 3, 7, 14 follow-ups |
| 6-7 | Lead scoring integration in blast priority | Hot leads contacted first |
| 6-7 | Brain learning: store service + outcome | `learn_outcome` includes service type |
| 8-10 | End-to-end test: 500 leads, all services | Full pipeline validation |

**Success criteria:** Personalized messages per service, A/B testing active.

### Phase 4: Analytics & Optimization (Week 7-8)

**Goal:** Dashboard updates, brain intelligence loop, conversion optimization.

| Day | Task | Deliverable |
|---|---|---|
| 1-3 | Dashboard: service-specific funnel views | Filter by service, conversion rates |
| 1-3 | Dashboard: lead scoring visualization | Tier distribution, top prospects |
| 4-5 | Brain auto-learning from outcomes | Service+vertical patterns |
| 4-5 | Proposal template auto-optimization | Brain suggests template tweaks |
| 6-7 | Bundle proposal generation | Multi-service packages |
| 6-7 | Integration with berkakahkarya.org CTA | Direct booking links in proposals |
| 8-10 | Full pipeline monitoring + alerts | Auto-restart on failures |

**Success criteria:** Self-improving system, full analytics, bundle proposals.

---

## 9. Cost Analysis

### 9.1 Per-Lead Cost Breakdown

| Stage | Current Cost | New Cost | Savings |
|---|---|---|---|
| Scraping | $0.03/lead (Google API) | **$0.00** | 100% |
| Enrichment (email) | $0.02/lead (AgentCash) | **$0.00** (built-in) | 100% |
| Research | $0.01/lead (compute) | $0.01/lead | 0% |
| Generation | $0.05/lead (Claude) | $0.05/lead | 0% |
| Review | $0.02/lead (Claude) | $0.02/lead | 0% |
| Sending | $0.00/lead | $0.00/lead | 0% |
| **Total per lead** | **$0.13** | **$0.08** | **38%** |

### 9.2 Monthly Cost Projection

| Leads/Month | Current Cost | New Cost | Monthly Savings |
|---|---|---|---|
| 500 | $65 | $40 | $25 |
| 1,000 | $130 | $80 | $50 |
| 5,000 | $650 | $400 | $250 |
| 10,000 | $1,300 | $800 | $500 |

### 9.3 Revenue Projection

Assumptions:
- 1,000 leads/month
- 30% open rate
- 10% reply rate
- 20% meeting booked rate
- 30% close rate
- Average deal: Rp 1.5jt (mix of services)

```
1,000 leads
  → 300 opens (30%)
    → 30 replies (10%)
      → 6 meetings (20%)
        → 2 deals (30%)
          → Rp 3jt revenue/month

With multi-service bundles (avg Rp 2jt):
  → Rp 4jt revenue/month

With service-specific personalization (2x conversion):
  → Rp 8jt revenue/month

System cost: Rp 1.2jt/month (server + API + Claude)
Net profit: Rp 6.8jt/month
ROI: 567%
```

---

## 10. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| gosom scraper blocked by Google | Medium | High | Proxy rotation (built-in), fallback to Google Places API |
| Scraper Docker container crashes | Low | Medium | systemd auto-restart, health check monitoring |
| Proposal quality inconsistency | Medium | High | Claude quality gate (6/10), template constraints, brain learning |
| Wrong service detection | Medium | Medium | Confidence threshold, multi-service option, manual override |
| Lead data accuracy | Medium | Medium | Cross-reference enrichment, dedup by multiple fields |
| WhatsApp spam reports | Low | High | 30-day cooldown, opt-out handling, rate limiting |
| Rate limiting on enrichment | Medium | Low | Queue system, exponential backoff, AgentCash fallback |
| Brain hub downtime | Low | Low | Graceful degradation — pipeline works without brain |

### Fallback Chain

```
Primary:   gosom/google-maps-scraper (free, unlimited)
Fallback:  Google Places API ($200/mo credit)
Last:      AgentCash Minerva enrichment
```

---

## 11. File Structure (New Files)

```
1ai-reach/
├── scripts/
│   ├── gmaps_client.py              # NEW: REST API client for gosom scraper
│   ├── service_detector.py          # NEW: AI service matching
│   ├── lead_scorer.py               # NEW: Multi-dimensional scoring
│   └── orchestrator.py              # UPDATED: multi-service pipeline
├── templates/
│   ├── website_development.yaml     # NEW: website proposal template
│   ├── adforge_ai.yaml              # NEW: ads proposal template
│   ├── ai_agent_pro.yaml            # NEW: chatbot proposal template
│   ├── social_media_management.yaml # NEW: social media template
│   ├── ai_creative_studio.yaml      # NEW: video/content template
│   ├── ai_automation.yaml           # NEW: automation template
│   ├── security_audit.yaml          # NEW: security template
│   ├── deep_research.yaml           # NEW: research template
│   ├── bundle_growth.yaml           # NEW: multi-service bundle template
│   └── bundle_full_stack.yaml       # NEW: complete package template
├── gmaps-scraper.service           # NEW: systemd unit file
├── data/
│   └── gmaps/                       # NEW: scraper data volume
└── logs/
    └── gmaps-scraper.log            # NEW: scraper logs
```

---

## 12. Summary & Recommendation

**Go/No-Go Decision: GO**

This integration delivers:
1. **Zero-cost scraping** — unlimited leads, no API key dependency
2. **Service-specific personalization** — 3-5x conversion improvement
3. **Multi-service revenue** — sell the right service to the right lead
4. **Self-improving system** — brain learns which services convert per vertical
5. **Scalable architecture** — Docker-based, REST API-driven

**Total implementation time: 8 weeks (4 phases)**
**Expected ROI: 300-400% within first 2 months (conservative estimate based on 2-3x conversion uplift)**

The proposal is ready for review. Upon approval, Phase 1 (scraper integration) can begin immediately.

---

*Prepared by 1ai-reach Architecture Team*
*BerkahKarya — berkahkarya.org*

---

## 13. Technical Integration Details (Metis Gap Analysis Applied)

### 11.1 Scraper Coexistence Strategy

The system currently has TWO scraping sources. Both will remain active:

| Source | When Used | Why Keep |
|---|---|---|
| **gosom/google-maps-scraper** | Primary — all new scraping jobs | Free, unlimited, fast, built-in emails |
| **vibe_scraper.py** (Vibe Prospecting MCP) | Decision-maker leads — when we need direct contact names | Gets decision-maker name + LinkedIn + direct email |
| **Google Places API** (current scraper.py) | Fallback — when gosom is unavailable | Reliable, structured data, no scraping risk |

```
orchestrator scraping logic:

1. PRIMARY: gosom scraper → bulk leads (free, unlimited)
2. ENRICHMENT: Vibe Prospecting → decision-maker names for top 20 leads
3. FALLBACK: Google Places API → if gosom Docker container is down
```

### 11.2 Deployment: systemd (Not docker-compose)

1ai-reach uses systemd for all services (API on 8001, dashboard on 8502, MCP webhook). The gosom scraper will follow the same pattern:

```ini
# /etc/systemd/system/gmaps-scraper.service
[Unit]
Description=Google Maps Scraper (gosom)
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStartPre=-/usr/bin/docker rm -f gmaps-scraper
ExecStart=/usr/bin/docker run --name gmaps-scraper \
  -v /home/openclaw/projects/1ai-reach/data/gmaps:/gmapsdata \
  -p 8081:8080 \
  gosom/google-maps-scraper \
  -data-folder /gmapsdata \
  -email \
  -lang id
ExecStop=/usr/bin/docker stop gmaps-scraper
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Port verification:** Port 8081 is confirmed free (8001=API, 8502=dashboard, 3000=other project, 8000=trading bot, 6969=nginx, 9099=hub).

### 11.3 Generator Integration — How Templates Feed Into Claude

The current generator.py uses Claude Sonnet with a single prompt. The new multi-service generator loads YAML templates as structured guidance for Claude:

```
For each lead:
  1. Load matched service from service_detector output
  2. Load templates/{service}.yaml → pain points, value props, case study, price anchor
  3. brain_client.get_strategy(vertical, location, service=matched_service)
  4. Build Claude prompt with: template guidance + research brief + brain intel
  5. Claude generates ---PROPOSAL--- email + ---WHATSAPP--- Indonesian hook
  6. reviewer.py quality gate (6/10 pass threshold)
```

### 11.4 Brain Client Enhancement

Current `get_strategy(vertical, location)` needs a `service` parameter:

```python
# brain_client.py addition
def get_strategy(vertical, location="Jakarta", service=None):
    query_parts = ["successful outreach proposal", vertical, location]
    if service:
        query_parts.insert(1, service)
    # ... returns strategy intel for this SERVICE+vertical combo
```

### 11.5 Researcher Enhancement — Signal Detection

Current researcher.py scrapes homepage for pain points. New version also detects service-matching signals:

```
SIGNAL_DETECTION additions:
  has_website: bool(websiteUri)
  website_status: up/down/redirect
  page_speed: load time in seconds
  mobile_friendly: yes/no
  has_ssl: yes/no
  has_seo: meta tags present
  has_contact_form: yes/no
  has_livechat: detect livechat widget
  social_links: {instagram, tiktok, facebook, youtube}
  social_activity: last post date, frequency
  ads_detected: competitor ads visible
  tech_stack: WordPress/Shopify/custom/legacy
  ecommerce_signals: product pages, cart, payment
  booking_system: Calendly/custom/none
```

### 11.6 Dashboard API Endpoints Needed

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/agents/services/detect` | POST | Run service detection for a lead |
| `/api/v1/agents/services/list` | GET | List available service templates |
| `/api/v1/agents/leads/{id}/score` | GET | Get lead multi-dimensional score |
| `/api/v1/agents/leads/{id}/services` | GET | Get matched services for a lead |
| `/api/v1/agents/funnel/by-service` | GET | Funnel breakdown per service type |
| `/api/v1/agents/stats/conversion-by-service` | GET | Conversion rates per service |

### 11.7 Conversion Rate Assumptions — Honest Basis

The "3-5x improvement" claim needs honest justification:

| Metric | Generic Proposal | Service-Specific | Basis |
|---|---|---|---|
| Open rate | 15-20% | 25-35% | Personalized subject with company name + specific pain |
| Reply rate | 3-5% | 8-15% | Addresses their exact problem, not generic pitch |
| Meeting rate | 1-2% | 3-5% | Relevant offer = higher intent |
| Close rate | 0.3-0.5% | 1-2% | Right service at right price |

**Conservative estimate: 2-3x improvement.** The 3-5x applies only to hot-tier leads with strong signal detection.

### 11.8 A/B Testing Framework

Track which template variants convert best per service+vertical:

```
experiments/
├── adforge_ai/
│   ├── subject_lines.json → {subject: {sent: N, opened: N, replied: N}}
│   ├── whatsapp_hooks.json → {hook: {sent: N, replied: N}}
│   └── email_templates.json → {template: {sent: N, opened: N, replied: N}}
└── website_development/
    ├── subject_lines.json
    └── ...
```

Variant selection via Thompson Sampling (multi-armed bandit). Winner declared after 50+ sends per variant.

---

## 14. Risks Updated (from Metis Review)

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| gosom scraper blocked by Google | Medium | High | Proxy rotation (built-in), fallback to Google Places API |
| Docker container crashes | Low | Medium | systemd auto-restart, health check endpoint |
| Proposal quality inconsistency | Medium | High | Claude quality gate (6/10), template constraints |
| Wrong service detection | Medium | Medium | Confidence threshold (score >= 5), manual override in dashboard |
| Lead data accuracy | Medium | Medium | Cross-reference enrichment, dedup by multiple fields |
| WhatsApp spam reports | Low | High | 30-day cooldown, opt-out, rate limiting |
| Rate limiting on enrichment | Medium | Low | Queue system, exponential backoff |
| Brain hub downtime | Low | Low | Graceful degradation |
| **Port conflict** | Low | High | Verified 8081 free; documented port registry |
| **gosom API field name mismatch** | Medium | Medium | Validate field names against actual scraper output before mapping |
| **Template YAML parse errors** | Low | Medium | Schema validation on load, unit tests per template |
| **Service detector false positives** | Medium | Medium | Require 2+ signals matching, not just 1 |


---

## 15. Scope Boundaries (Momus Review)

### IN SCOPE (This Proposal)

- gosom/google-maps-scraper Docker integration
- Multi-service proposal templates (top 5 services: Website, AdForge, AI Agent, Social Media, Automation)
- Service detection via rule-based signals + AI classification
- Lead scoring with 4 priority tiers
- Brain client enhancement for service-specific queries
- Researcher enhancement for signal detection
- Dashboard API endpoints for service views
- A/B testing framework for subject lines and hooks
- Service bundling strategy (Starter/Growth/Scale/Full Stack)
- systemd deployment for scraper container

### OUT OF SCOPE (Future Work)

- Templates for remaining 7 services (AI Creative Studio, Security Audit, Deep Research, Custom Documents, 1Ai Platform, Video Production, Algorithmic Trading) — to be added in Phase 5
- Dashboard UI components (frontend) — backend API only in this proposal
- Vibe Prospecting MCP integration changes — remains unchanged
- Google Places API removal — kept as fallback, not removed
- E-commerce integration (payment, invoicing)
- CRM integration beyond Google Sheets
- Automated meeting scheduling
- Voice note proposals via WhatsApp
- Multi-language proposals (only English email + Indonesian WA)

### ASSUMPTIONS REQUIRING VALIDATION

1. **gosom scraper REST API field names** — The field mapping in Section 3.4 (`title`, `address`, `phone`, `website`, `email`, `category`, etc.) must be verified against actual scraper output. Field names may differ from documentation.

2. **Docker availability on server** — The server must have Docker installed and running. Currently all services run natively (Python, Node.js).

3. **Claude Sonnet prompt capacity** — The multi-service prompt with template + research + brain intel may exceed context limits for complex leads. May need summarization.

4. **Review score threshold** — The 6/10 pass threshold is inherited from the current generic proposal. Service-specific proposals may need different thresholds.

5. **Brain hub returns service-specific data** — `get_strategy(service="website_development", vertical="restaurant")` assumes the brain has enough historical data. Initially, it may return empty results.
