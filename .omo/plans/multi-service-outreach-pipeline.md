# Multi-Service Outreach Pipeline — gosom Scraper + Service-Specific Proposals

## TL;DR

> **Quick Summary**: Integrate gosom/google-maps-scraper (free, 3.6K stars) as primary scraping engine and build multi-service proposal pipelines that auto-detect which BerkahKarya service each lead needs, then generate hyper-personalized proposals.
> 
> **Deliverables**:
> - gosom scraper Docker container + systemd service + Python REST API client
> - Service detector module (AI + rule-based signal matching)
> - Lead scorer module (7 dimensions, 4 priority tiers)
> - 5 YAML proposal templates (Website, AdForge, AI Agent, Social Media, Automation)
> - Enhanced researcher with signal detection
> - Enhanced brain client with service parameter
> - Enhanced generator for multi-service proposals
> - 6 new API endpoints for dashboard
> - A/B testing framework for templates
> 
> **Estimated Effort**: Large (8 weeks, 4 phases)
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Scraper deploy → client wrapper → service detector → templates → generator enhancement

---

## Context

### Original Request
User asked about open-source repos for Google Maps/business scraping to help with outreach. Found gosom/google-maps-scraper (MIT, 3.6K stars, free). Then user asked for comprehensive multi-service proposal system covering all BerkahKarya services.

### Interview Summary
**Key Discussions**:
- Scraper choice: gosom/google-maps-scraper selected over omkarcloud (paid) and others
- Service catalog: 12 BerkahKarya services from Rp 49K to Rp 2.5jt
- Personalization: Each lead gets auto-matched to 1-2 best-fit services
- Templates: Top 5 services get full proposal templates (email + WhatsApp)
- Bundling: Starter/Growth/Scale/Full Stack packages
- Brain integration: Store service-specific outcomes for learning

**Research Findings**:
- gosom scraper: REST API at port 8080, Docker, `-email` flag for email extraction, 120 places/min
- BerkahKarya (berkakahkarya.org): 12+ services, AI-first positioning
- Current pipeline: Google Places API costs $200/mo, capped at 6K searches
- Port 8081 confirmed free for scraper container

### Metis Review
**Identified Gaps** (addressed):
- Scraper coexistence strategy (vibe_scraper + gosom + Google API fallback)
- systemd deployment (not docker-compose — matches existing infra)
- Generator integration detail (how templates feed Claude prompt)
- Brain client service parameter needed
- Dashboard API endpoints needed
- Conversion rate claims revised to conservative 2-3x
- A/B testing framework designed
- Scope boundaries explicit (IN/OUT)
- 5 assumptions requiring validation listed

### Reference Document
Full strategic proposal with architecture diagrams, all templates, cost analysis: 
`/home/openclaw/projects/1ai-reach/PROPOSAL_MULTI_SERVICE_PIPELINE.md` (1,466 lines)

---

## Work Objectives

### Core Objective
Replace paid Google Places API with free gosom scraper and build a multi-service proposal system that auto-matches each lead to the best BerkahKarya service and generates service-specific personalized proposals.

### Concrete Deliverables
- `scripts/gmaps_client.py` — Python REST API client for gosom scraper
- `/etc/systemd/system/gmaps-scraper.service` — systemd unit for Docker container
- `scripts/service_detector.py` — Signal-based service matching engine
- `scripts/lead_scorer.py` — Multi-dimensional lead scoring
- `templates/website_development.yaml` — Website proposal template
- `templates/adforge_ai.yaml` — Ads management proposal template
- `templates/ai_agent_pro.yaml` — Chatbot proposal template
- `templates/social_media_management.yaml` — Social media proposal template
- `templates/ai_automation.yaml` — Automation proposal template
- `scripts/generator.py` updated — Multi-service template-aware generation
- `scripts/brain_client.py` updated — Service-specific strategy queries
- `scripts/researcher.py` updated — Signal detection for service matching
- 6 new API endpoints in FastAPI backend
- A/B testing module for template variant optimization

### Definition of Done
- [ ] `curl http://localhost:8082/api/v1/jobs` returns scraper API (Docker running)
- [ ] `oneai-reach scrape "Digital Agency in Jakarta"` uses gosom scraper, inserts leads
- [ ] Each lead gets `matched_services` field with 1-2 ranked services
- [ ] Each lead gets `lead_score` with tier (hot/warm/cold/skip)
- [ ] Proposals are service-specific (website leads get website template, etc.)
- [ ] `brain_client.get_strategy(vertical="restaurant", service="website_development")` works
- [ ] Dashboard shows funnel breakdown by service type
- [ ] All existing pipeline stages still work (no regressions)

### Must Have
- gosom scraper running as Docker container via systemd
- Service detector with minimum confidence threshold (score >= 5)
- At least 5 complete proposal templates with email + WhatsApp
- Lead scoring with 4 tiers
- Brain client enhancement for service queries
- Fallback to Google Places API if scraper is down
- All existing functionality preserved (no regressions)

### Must NOT Have (Guardrails)
- Do NOT remove Google Places API or vibe_scraper — they are fallback/secondary sources
- Do NOT use port 8000 (trading bot), 3000 (other project), 8502 (dashboard), or 8001 (API)
- Do NOT modify existing funnel stages status flow
- Do NOT change existing leads.db schema — only ADD columns (matched_services, lead_score, tier, service_proposed)
- Do NOT send proposals without reviewer.py quality gate (6/10 threshold)
- Do NOT add excessive comments or over-engineer — keep it practical
- Do NOT hardcode URLs or API keys — use config.py for all settings
- Do NOT create docker-compose.yml — use systemd like all other services

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest/vitest available)
- **Automated tests**: Tests-after (implement first, then add regression tests)
- **Framework**: pytest for Python, bun test for dashboard
- **Agent-Executed QA**: ALWAYS (mandatory for all tasks)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/Backend**: Use Bash (curl) — Send requests, assert status + response fields
- **Python modules**: Use Bash (python3 -c) — Import, call functions, verify output
- **Docker services**: Use Bash — Check container status, API health
- **Templates**: Use Bash — Validate YAML parse, check required fields

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation + infrastructure):
├── Task 1: Deploy gosom scraper Docker container [quick]
├── Task 2: Build gmaps_client.py REST API wrapper [unspecified-high]
├── Task 3: Create 5 YAML proposal templates [quick]
└── Task 4: Add new columns to leads.db schema [quick]

Wave 2 (After Wave 1 — core intelligence modules, MAX PARALLEL):
├── Task 5: Build service_detector.py (depends: 4) [deep]
├── Task 6: Build lead_scorer.py (depends: 4) [unspecified-high]
├── Task 7: Enhance researcher.py with signal detection (depends: 4) [unspecified-high]
├── Task 8: Enhance brain_client.py with service parameter (depends: 3) [quick]
└── Task 9: Build A/B testing module (depends: 3) [unspecified-high]

Wave 3 (After Wave 2 — integration + generation):
├── Task 10: Update generator.py for multi-service (depends: 5, 8, 9) [deep]
├── Task 11: Update orchestrator.py for new scraper (depends: 2, 5, 6) [deep]
├── Task 12: Add 6 new API endpoints (depends: 5, 6, 4) [unspecified-high]
├── Task 13: Update dashboard frontend for service views (depends: 12) [visual-engineering]
└── Task 14: Integration test — full pipeline with 10 leads (depends: 10, 11) [deep]

Wave FINAL (After ALL tasks — verification):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: End-to-end QA with 50 real leads [unspecified-high]
└── Task F4: Scope fidelity check [deep]
```

### Dependency Matrix

| Task | Depends On | Blocks |
|---|---|---|
| 1 | — | 2, 11 |
| 2 | 1 | 11 |
| 3 | — | 8, 9 |
| 4 | — | 5, 6, 7 |
| 5 | 4 | 10, 12 |
| 6 | 4 | 11, 12 |
| 7 | 4 | 10 |
| 8 | 3 | 10 |
| 9 | 3 | 10 |
| 10 | 5, 7, 8, 9 | 14 |
| 11 | 2, 5, 6 | 14 |
| 12 | 5, 6, 4 | 13 |
| 13 | 12 | F3 |
| 14 | 10, 11 | F3 |

### Agent Dispatch Summary

- **Wave 1**: 4 tasks — T1→`quick`, T2→`unspecified-high`, T3→`quick`, T4→`quick`
- **Wave 2**: 5 tasks — T5→`deep`, T6→`unspecified-high`, T7→`unspecified-high`, T8→`quick`, T9→`unspecified-high`
- **Wave 3**: 5 tasks — T10→`deep`, T11→`deep`, T12→`unspecified-high`, T13→`visual-engineering`, T14→`deep`
- **Wave FINAL**: 4 tasks — F1→`oracle`, F2→`unspecified-high`, F3→`unspecified-high`, F4→`deep`

---

## TODOs

- [x] 1. Deploy gosom Scraper Docker Container

  **What to do**:
  - Create systemd service file at `/etc/systemd/system/gmaps-scraper.service`
  - Create data directory: `mkdir -p /home/openclaw/projects/1ai-reach/data/gmaps`
  - Pull Docker image: `docker pull gosom/google-maps-scraper:latest`
  - Start the container via systemd: `systemctl enable --now gmaps-scraper`
  - Verify API responds: `curl http://localhost:8082/api/v1/jobs`
  - Test a scrape: `curl -X POST http://localhost:8082/api/v1/jobs -d '{"query":"Coffee Shop Jakarta"}'`

  **Must NOT do**:
  - Do NOT use port 8000, 3000, 8502, 8001
  - Do NOT create docker-compose.yml
  - Do NOT hardcode any URLs

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Tasks 2, 11
  - **Blocked By**: None

  **References**:
  - `/etc/systemd/system/1ai-reach-dashboard.service` — existing systemd service pattern to follow
  - `/home/openclaw/projects/1ai-reach/scripts/config.py` — for PORT constants
  - gosom scraper docs: https://github.com/gosom/google-maps-scraper — REST API endpoints and Docker flags
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.2 — systemd unit file template

  **Acceptance Criteria**:
  - [ ] `systemctl status gmaps-scraper` shows active (running)
  - [ ] `curl -s http://localhost:8082/api/v1/jobs` returns JSON (empty list or job data)
  - [ ] `ss -tlnp | grep 8081` shows the Docker proxy listening

  **QA Scenarios**:
  ```
  Scenario: Scraper API is reachable
    Tool: Bash (curl)
    Steps:
      1. curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/api/v1/jobs
    Expected Result: HTTP 200
    Evidence: .sisyphus/evidence/task-1-scraper-health.txt

  Scenario: Scraper can create a job
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://localhost:8082/api/v1/jobs -H "Content-Type: application/json" -d '{"query":"Cafe Jakarta","max":5}'
      2. Extract job_id from response
    Expected Result: Returns JSON with job id
    Evidence: .sisyphus/evidence/task-1-scraper-job.txt

  Scenario: Service restarts on failure
    Tool: Bash
    Steps:
      1. docker kill gmaps-scraper
      2. sleep 15
      3. systemctl status gmaps-scraper
    Expected Result: Service auto-restarts (systemd Restart=always)
    Evidence: .sisyphus/evidence/task-1-restart.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `feat(scraper): deploy gosom scraper Docker container`
  - Files: `gmaps-scraper.service`

- [x] 2. Build gmaps_client.py REST API Wrapper

  **What to do**:
  - Create `scripts/gmaps_client.py` with class `GmapsScraperClient`
  - Methods: `create_job(query, max_results)`, `poll_job(job_id, timeout)`, `download_results(job_id)`, `scrape(query, max_results)`, `map_to_lead(raw)`
  - Add `GMAPS_SCRAPER_URL` to `scripts/config.py` (default: `http://localhost:8082`)
  - Field mapping: gosom output → leads.db schema (place_id→id, title→displayName, etc.)
  - Error handling: connection timeout, scraper down, empty results
  - Test with real scraper: `python3 -c "from scripts.gmaps_client import GmapsScraperClient; c=GmapsScraperClient(); print(c.scrape('Cafe Jakarta', 5))"`

  **Must NOT do**:
  - Do NOT hardcode localhost:8082 — use config.py constant
  - Do NOT modify leads.db insertion logic (that's Task 11)
  - Do NOT add the scraper as dependency to existing scraper.py

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (after Task 1 is deployed)
  - **Parallel Group**: Wave 1 (with Tasks 3, 4)
  - **Blocks**: Task 11
  - **Blocked By**: Task 1

  **References**:
  - `scripts/config.py` — Add `GMAPS_SCRAPER_URL` constant alongside existing `HUB_URL`
  - `scripts/leads.py` — `load_leads()` and `save_leads()` for understanding lead schema
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 3.4 — Python client wrapper pseudocode with field mapping
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.2 — Port configuration
  - gosom scraper API: `POST /api/v1/jobs` body `{"query":"...", "max": N}`, response includes `id`

  **Acceptance Criteria**:
  - [ ] `python3 -c "from scripts.gmaps_client import GmapsScraperClient"` imports without error
  - [ ] `GmapsScraperClient().scrape("Cafe Jakarta", 5)` returns list of dicts with mapped fields
  - [ ] `GMAPS_SCRAPER_URL` in config.py, not hardcoded in client

  **QA Scenarios**:
  ```
  Scenario: Client scrapes real data from gosom API
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.gmaps_client import GmapsScraperClient; c=GmapsScraperClient(); results=c.scrape('Cafe Jakarta', 5); print(len(results), results[0].keys())"
    Expected Result: Returns 3-5 results with keys: id, displayName, formattedAddress, phone, websiteUri, email, primaryType, source
    Evidence: .sisyphus/evidence/task-2-client-scrape.txt

  Scenario: Client handles scraper down gracefully
    Tool: Bash (python3)
    Steps:
      1. Stop gosom container temporarily
      2. python3 -c "from scripts.gmaps_client import GmapsScraperClient; c=GmapsScraperClient('http://localhost:9999'); c.scrape('test', 1)"
    Expected Result: Raises ConnectionError or returns empty list (not crash without message)
    Evidence: .sisyphus/evidence/task-2-client-down.txt

  Scenario: Field mapping produces valid lead dict
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.gmaps_client import GmapsScraperClient; lead=GmapsScraperClient.map_to_lead({'place_id':'test123','title':'Test Cafe','address':'Jakarta','phone':'021123','category':'cafe'}); print(lead['id'], lead['displayName'], lead['source'])"
    Expected Result: id='test123', displayName='Test Cafe', source='gmaps_scraper'
    Evidence: .sisyphus/evidence/task-2-field-mapping.txt
  ```

  **Commit**: YES (groups with Task 1)
  - Message: `feat(scraper): add gosom scraper Docker deployment and Python client`
  - Files: `scripts/gmaps_client.py`, `scripts/config.py`

- [x] 3. Create 5 YAML Proposal Templates

  **What to do**:
  - Create `templates/` directory at project root
  - Create 5 YAML files with full proposal content (see PROPOSAL document sections 6.1-6.5):
    1. `templates/website_development.yaml`
    2. `templates/adforge_ai.yaml`
    3. `templates/ai_agent_pro.yaml`
    4. `templates/social_media_management.yaml`
    5. `templates/ai_automation.yaml`
  - Each template must have: service, service_name_display, price_display, price_anchor, target_signals, pain_points, value_props, case_study, email (subject_lines + body_template), whatsapp (templates list of 3), cta
  - Validate all YAML files parse correctly

  **Must NOT do**:
  - Do NOT create templates for services beyond the 5 listed
  - Do NOT include hardcoded company names or URLs in templates
  - Do NOT add excessive comments in YAML

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`writing-skills`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Tasks 8, 9
  - **Blocked By**: None

  **References**:
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 6.1 — website_development.yaml full example (copy exactly)
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 6.2 — adforge_ai.yaml full example
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 6.3 — ai_agent_pro.yaml full example
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 6.4 — social_media_management.yaml full example
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 6.5 — ai_automation.yaml full example
  - berkakahkarya.org — service pricing and value props (already captured in proposal)

  **Acceptance Criteria**:
  - [ ] `python3 -c "import yaml; [yaml.safe_load(open(f'templates/{t}')) for t in ['website_development.yaml','adforge_ai.yaml','ai_agent_pro.yaml','social_media_management.yaml','ai_automation.yaml']]"` succeeds
  - [ ] Each template has all required fields: service, price_display, pain_points, value_props, email.subject_lines (4+), whatsapp.templates (3+), cta

  **QA Scenarios**:
  ```
  Scenario: All 5 templates parse as valid YAML
    Tool: Bash (python3)
    Steps:
      1. python3 -c "
import yaml, os
required = ['service','price_display','pain_points','value_props','email','whatsapp','cta']
for t in ['website_development','adforge_ai','ai_agent_pro','social_media_management','ai_automation']:
    with open(f'templates/{t}.yaml') as f: d=yaml.safe_load(f)
    missing = [k for k in required if k not in d]
    if missing: print(f'{t}: MISSING {missing}')
    else: print(f'{t}: OK')
"
    Expected Result: All 5 print "OK"
    Evidence: .sisyphus/evidence/task-3-templates-valid.txt

  Scenario: Templates have sufficient variety in subject lines and WA hooks
    Tool: Bash (python3)
    Steps:
      1. python3 -c "
import yaml
for t in ['website_development','adforge_ai','ai_agent_pro','social_media_management','ai_automation']:
    with open(f'templates/{t}.yaml') as f: d=yaml.safe_load(f)
    subs = d['email']['subject_lines']
    was = d['whatsapp']['templates']
    print(f'{t}: {len(subs)} subject lines, {len(was)} WA hooks')
"
    Expected Result: Each template has >= 3 subject lines and >= 2 WA hooks
    Evidence: .sisyphus/evidence/task-3-template-counts.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(templates): add 5 service-specific proposal templates`
  - Files: `templates/*.yaml`

- [x] 4. Add New Columns to leads.db Schema

  **What to do**:
  - Add columns to the leads table in SQLite: `matched_services TEXT` (JSON array), `lead_score REAL`, `tier TEXT`, `service_proposed TEXT`
  - Update `scripts/state_manager.py` or equivalent to handle new columns on insert/query
  - Migration must be backward-compatible — existing 123 leads get NULL for new columns (they can be scored on-demand)
  - Update Lead Pydantic model if one exists in `src/oneai_reach/domain/models/`

  **Must NOT do**:
  - Do NOT change or remove any existing columns
  - Do NOT drop and recreate the table
  - Do NOT break existing leads (123 leads must remain intact)
  - Do NOT add foreign keys or constraints that break existing data

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Tasks 5, 6, 7
  - **Blocked By**: None

  **References**:
  - `scripts/state_manager.py` or `scripts/leads.py` — current DB schema and access patterns
  - `data/leads.db` — SQLite database with 123 leads
  - `src/oneai_reach/domain/models/` — Pydantic domain models if they exist
  - `src/oneai_reach/infrastructure/database/` — repository implementations

  **Acceptance Criteria**:
  - [ ] `sqlite3 data/leads.db ".schema leads"` shows new columns (matched_services, lead_score, tier, service_proposed)
  - [ ] `sqlite3 data/leads.db "SELECT COUNT(*) FROM leads"` still returns 123
  - [ ] Existing API endpoints still return lead data correctly

  **QA Scenarios**:
  ```
  Scenario: Schema migration preserves existing data
    Tool: Bash (sqlite3)
    Steps:
      1. sqlite3 data/leads.db "SELECT COUNT(*) FROM leads"
      2. sqlite3 data/leads.db "SELECT matched_services, lead_score, tier, service_proposed FROM leads LIMIT 1"
    Expected Result: COUNT=123, new columns are NULL for existing leads
    Evidence: .sisyphus/evidence/task-4-schema-migration.txt

  Scenario: New columns can be updated
    Tool: Bash (sqlite3)
    Steps:
      1. sqlite3 data/leads.db "UPDATE leads SET matched_services='[\"website_development\"]', lead_score=7.5, tier='warm', service_proposed='website_development' WHERE rowid=1"
      2. sqlite3 data/leads.db "SELECT matched_services, lead_score, tier FROM leads WHERE rowid=1"
    Expected Result: Returns the inserted values
    Evidence: .sisyphus/evidence/task-4-column-update.txt
    (Rollback after test: set back to NULL)
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(schema): add service detection columns to leads table`
  - Files: migration script or updated schema

- [x] 5. Build service_detector.py — Signal-Based Service Matching

  **What to do**:
  - Create `scripts/service_detector.py` with function `detect_services(lead, research) -> list[dict]`
  - Implement SERVICE_SIGNALS dict from PROPOSAL Section 5.3 (7 services, each with weighted signals)
  - Each signal checked against lead data + research data (e.g., `no_website = not lead.get("websiteUri")`)
  - Vertical boost: 1.3x multiplier if lead's primaryType matches service target_verticals
  - Brain boost: 1.2x if brain_client has strategy for this service+vertical
  - Return top 2 services with score >= 5.0 (minimum confidence threshold)
  - Return format: `[{"service": "website_development", "score": 9.5, "reasons": ["no_website"]}]`

  **Must NOT do**:
  - Do NOT call external APIs for every detection (brain_client is optional, cache results)
  - Do NOT hardcode business names or locations
  - Do NOT return more than 2 services per lead (avoid overwhelming)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: Tasks 10, 12
  - **Blocked By**: Task 4

  **References**:
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 5.3 — Full SERVICE_SIGNALS dict with 7 services and all signal weights
  - `scripts/brain_client.py:86` — `get_strategy(vertical, location)` function to add `service` param to (Task 8 does this)
  - `scripts/config.py` — for any needed constants

  **Acceptance Criteria**:
  - [ ] `python3 -c "from scripts.service_detector import detect_services; print(detect_services({'websiteUri':'','reviewCount':150,'primaryType':'restaurant','phone':'021123'},{'social_links':[]}))"` returns list with website_development
  - [ ] Score is float >= 0, reasons list is non-empty when score >= 5
  - [ ] Returns empty list when no signals match

  **QA Scenarios**:
  ```
  Scenario: Lead with no website gets website_development
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.service_detector import detect_services; r=detect_services({'websiteUri':'','reviewCount':150,'primaryType':'restaurant'},{}); print(r[0]['service'], r[0]['score'])"
    Expected Result: First result is 'website_development' with score >= 8
    Evidence: .sisyphus/evidence/task-5-detect-website.txt

  Scenario: Lead with website + many reviews gets ai_agent_pro
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.service_detector import detect_services; r=detect_services({'websiteUri':'http://example.com','reviewCount':500,'primaryType':'clinic','has_livechat':False},{}); print([s['service'] for s in r])"
    Expected Result: List includes 'ai_agent_pro'
    Evidence: .sisyphus/evidence/task-5-detect-agent.txt

  Scenario: No matching signals returns empty
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.service_detector import detect_services; r=detect_services({'websiteUri':'http://perfect.com','reviewCount':10,'primaryType':'lawyer'},{})"; print(len(r))
    Expected Result: 0 or only very low scores (< 5)
    Evidence: .sisyphus/evidence/task-5-detect-empty.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(detection): add service detector with signal-based matching`
  - Files: `scripts/service_detector.py`

- [x] 6. Build lead_scorer.py — Multi-Dimensional Lead Scoring

  **What to do**:
  - Create `scripts/lead_scorer.py` with function `score_lead(lead, research) -> dict`
  - 7 dimensions: digital_presence (20%), social_maturity (15%), ad_activity (15%), customer_volume (15%), response_readiness (10%), business_size (15%), match_score (10%)
  - Each dimension scored 0-10 with details string
  - Weighted total → tier assignment: hot (>=8), warm (>=5), cold (>=3), skip (<3)
  - Include recommended_services from service_detector in output

  **Must NOT do**:
  - Do NOT make network calls inside scorer (use pre-fetched research data)
  - Do NOT modify the lead in the database (scorer returns scores, caller decides whether to store)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 11, 12
  - **Blocked By**: Task 4

  **References**:
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 7 — Full scoring dimensions, weights, tier thresholds
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 7.3 — score_lead() pseudocode

  **Acceptance Criteria**:
  - [ ] `score_lead({'websiteUri':'','reviewCount':200},{})` returns dict with total_score, tier, and all 7 dimension scores
  - [ ] Tier is one of: hot, warm, cold, skip

  **QA Scenarios**:
  ```
  Scenario: Lead with no website + many reviews scores as hot/warm
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.lead_scorer import score_lead; r=score_lead({'websiteUri':'','reviewCount':200,'primaryType':'restaurant','formattedAddress':'Jakarta'},{}); print(r['total_score'], r['tier'])"
    Expected Result: total_score >= 5, tier in ['hot','warm']
    Evidence: .sisyphus/evidence/task-6-score-hot.txt

  Scenario: Lead with perfect digital presence scores lower urgency
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.lead_scorer import score_lead; r=score_lead({'websiteUri':'https://perfect.com','reviewCount':50,'primaryType':'lawyer'},{}); print(r['tier'])"
    Expected Result: tier in ['warm','cold'] (less urgent needs)
    Evidence: .sisyphus/evidence/task-6-score-cold.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(scoring): add multi-dimensional lead scorer with tier classification`
  - Files: `scripts/lead_scorer.py`

- [x] 7. Enhance researcher.py with Signal Detection

  **What to do**:
  - Extend existing researcher.py to detect service-matching signals alongside pain points
  - Add signal detection for: has_website, website_status, page_speed, mobile_friendly, has_ssl, has_seo, has_contact_form, has_livechat, social_links, social_activity, ads_detected, tech_stack, ecommerce_signals, booking_system
  - Store signals in research brief (data/research/{index}_{name}.txt) as structured section
  - These signals feed into service_detector.py

  **Must NOT do**:
  - Do NOT break existing research functionality (pain point detection, service listing, tech stack)
  - Do NOT add dependencies on external services that require API keys
  - Do NOT slow down research phase significantly (signal detection should add <5s per lead)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 10
  - **Blocked By**: Task 4

  **References**:
  - `scripts/researcher.py` — current research logic to extend
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.5 — SIGNAL_DETECTION dict with 14 signals to detect
  - `data/research/` — existing research brief files for format reference

  **Acceptance Criteria**:
  - [ ] Research brief for a lead contains a "SIGNALS:" section with detected signals
  - [ ] Existing pain points, services, tech stack detection still works
  - [ ] Signal detection runs without errors on leads with and without websites

  **QA Scenarios**:
  ```
  Scenario: Research detects signals for a lead with website
    Tool: Bash (python3)
    Steps:
      1. Run researcher on a lead with a website (e.g., any of the existing 123 leads)
      2. Check research brief for "SIGNALS:" section
    Expected Result: Brief contains signals like has_website=True, tech_stack=..., has_ssl=...
    Evidence: .sisyphus/evidence/task-7-signals-detected.txt

  Scenario: Research handles lead without website
    Tool: Bash (python3)
    Steps:
      1. Run researcher on a lead with empty websiteUri
      2. Check that has_website=False and other signals are detected without crash
    Expected Result: has_website=False, no errors
    Evidence: .sisyphus/evidence/task-7-no-website.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(research): add service-matching signal detection to researcher`
  - Files: `scripts/researcher.py`

- [x] 8. Enhance brain_client.py with Service Parameter

  **What to do**:
  - Add `service` parameter to `get_strategy()` function (optional, default=None)
  - When service is provided, include it in the search query: `"successful outreach proposal {service} {vertical} {location}"`
  - Update `learn_outcome()` to accept and store `service_type` parameter
  - Backward compatible — existing calls without service param still work

  **Must NOT do**:
  - Do NOT break existing brain_client API (all current calls must still work)
  - Do NOT change return types

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 10
  - **Blocked By**: Task 3 (templates must exist to know service names)

  **References**:
  - `scripts/brain_client.py:86-103` — current `get_strategy()` function
  - `scripts/brain_client.py:106-142` — current `learn_outcome()` function
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.4 — enhancement pseudocode

  **Acceptance Criteria**:
  - [ ] `brain_client.get_strategy("restaurant", "Jakarta", service="website_development")` works
  - [ ] `brain_client.get_strategy("restaurant")` still works (backward compatible)
  - [ ] `brain_client.learn_outcome("Test", "restaurant", "replied", service_type="website_development")` stores service info

  **QA Scenarios**:
  ```
  Scenario: Service-specific strategy query works
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.brain_client import get_strategy; print(get_strategy('restaurant', 'Jakarta', service='website_development'))"
    Expected Result: Returns string (possibly empty if no data yet, but no error)
    Evidence: .sisyphus/evidence/task-8-brain-service.txt

  Scenario: Backward compatible — old calls still work
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.brain_client import get_strategy; print(get_strategy('restaurant', 'Jakarta'))"
    Expected Result: Returns string (same as before)
    Evidence: .sisyphus/evidence/task-8-brain-compat.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(brain): add service parameter to strategy queries`
  - Files: `scripts/brain_client.py`

- [x] 9. Build A/B Testing Module

  **What to do**:
  - Create `scripts/ab_testing.py` with class `ProposalABTest`
  - Methods: `select_variant(service, variant_type, vertical)`, `record_outcome(service, variant_type, variant, outcome)`, `get_winner(service, variant_type)`
  - Store stats in JSON files under `data/experiments/{service}/`
  - Variant selection: Thompson Sampling (multi-armed bandit)
  - Winner declared after 50+ sends per variant

  **Must NOT do**:
  - Do NOT use a database for A/B stats — simple JSON files are sufficient
  - Do NOT add external dependencies

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 10
  - **Blocked By**: Task 3 (templates must exist)

  **References**:
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.8 — A/B testing design
  - `templates/*.yaml` — each has `email.subject_lines` (4+) and `whatsapp.templates` (3+) — these are the variants

  **Acceptance Criteria**:
  - [ ] `ProposalABTest().select_variant("website_development", "subject_lines", "restaurant")` returns a string
  - [ ] `ProposalABTest().record_outcome("website_development", "subject_lines", "line1", "sent")` creates/updates JSON file
  - [ ] Stats files created under `data/experiments/`

  **QA Scenarios**:
  ```
  Scenario: Variant selection works
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.ab_testing import ProposalABTest; ab=ProposalABTest(); v=ab.select_variant('website_development','subject_lines','restaurant'); print(type(v), len(v) > 0)"
    Expected Result: Returns a non-empty string
    Evidence: .sisyphus/evidence/task-9-ab-select.txt

  Scenario: Recording outcomes and getting winner
    Tool: Bash (python3)
    Steps:
      1. Record 60 sends and 10 replies for variant A, 60 sends and 5 replies for variant B
      2. Call get_winner()
    Expected Result: Returns variant A (higher reply rate)
    Evidence: .sisyphus/evidence/task-9-ab-winner.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(ab): add proposal A/B testing with Thompson Sampling`
  - Files: `scripts/ab_testing.py`

- [x] 10. Update generator.py for Multi-Service Proposals

  **What to do**:
  - Modify `scripts/generator.py` to load service-specific YAML templates based on lead's `matched_services`
  - After service_detector identifies services, generator loads the corresponding template from `templates/{service}.yaml`
  - Inject template data into Claude prompt: pain points, value props, case study, CTA
  - Use A/B testing module to select subject line and WhatsApp hook variants
  - Brain client query includes service parameter: `get_strategy(vertical, location, service=service)`
  - Output format stays the same: `---PROPOSAL---` email body + `---WHATSAPP---` WA message
  - Fallback: if no service matched or template missing, use generic proposal (current behavior)

  **Must NOT do**:
  - Do NOT change the output format (---PROPOSAL--- / ---WHATSAPP---)
  - Do NOT break existing generator for leads without matched_services
  - Do NOT skip the reviewer.py quality gate

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential first task)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 5, 7, 8, 9

  **References**:
  - `scripts/generator.py` — current generation logic (loads research brief, calls Claude)
  - `scripts/generator.py` — backward compat shim, real logic in `src/oneai_reach/application/outreach/`
  - `templates/*.yaml` — YAML templates created in Task 3 (email body_template, whatsapp templates)
  - `scripts/ab_testing.py` — created in Task 9, `select_variant()` for subject/WA variant
  - `scripts/brain_client.py` — enhanced in Task 8 with `service` param
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 8 — generator enhancement design
  - PROPOSAL_MULTI_SERVICE_PIPELINE.md Section 13.3 — prompt template with service injection

  **Acceptance Criteria**:
  - [ ] `python3 scripts/generator.py` generates service-specific proposals for leads with matched_services
  - [ ] Proposal content references service-specific pain points and value props from template
  - [ ] Leads without matched_services still get generic proposals (backward compatible)
  - [ ] Each proposal file in `proposals/drafts/` contains both ---PROPOSAL--- and ---WHATSAPP--- sections

  **QA Scenarios**:
  ```
  Scenario: Generator produces service-specific proposal for lead with matched_services
    Tool: Bash (python3)
    Steps:
      1. Set a lead's matched_services='["website_development"]' in DB
      2. Run: python3 scripts/generator.py --lead-id {that_lead_id}
      3. Read the generated proposal file from proposals/drafts/
    Expected Result: Proposal mentions website-related pain points, references website_development pricing
    Evidence: .sisyphus/evidence/task-10-service-proposal.txt

  Scenario: Generator fallback for lead without matched_services
    Tool: Bash (python3)
    Steps:
      1. Use an existing lead with matched_services=NULL
      2. Run: python3 scripts/generator.py --lead-id {that_lead_id}
      3. Read proposal file
    Expected Result: Generic proposal generated (same format as before enhancement)
    Evidence: .sisyphus/evidence/task-10-generic-proposal.txt

  Scenario: WhatsApp section uses template variant
    Tool: Bash (python3)
    Steps:
      1. Generate proposal for lead with matched_services='["adforge_ai"]'
      2. Check ---WHATSAPP--- section content
    Expected Result: WA message references ads/AdForge value props from template
    Evidence: .sisyphus/evidence/task-10-whatsapp-variant.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(generator): multi-service template-aware proposal generation`
  - Files: `scripts/generator.py`

- [x] 11. Update orchestrator.py for New Scraper Integration

  **What to do**:
  - Modify `scripts/orchestrator.py` (or the real CLI at `src/oneai_reach/cli/main.py`) to add gosom scraper as primary source
  - New scrape stage: call `gmaps_client.scrape(query, max_results)` → insert leads via `leads.save_leads()`
  - Deduplication: check existing leads by websiteUri and email before inserting
  - After scraping, run service_detector on all new leads → update matched_services column
  - After service detection, run lead_scorer on all new leads → update lead_score and tier columns
  - Pipeline order: gosom scrape → service detect → score → enrich → research → generate → review → send
  - Keep existing `--dry-run`, `--followup-only`, `--enrich-only`, `--sync-only` flags working
  - Add `--scraper-source` flag: choices `gmaps` (default), `google-places`, `vibe` — selects scraper engine

  **Must NOT do**:
  - Do NOT remove existing scraper stages (Google Places, vibe_scraper)
  - Do NOT change existing CLI flags or their behavior
  - Do NOT break the pipeline for existing leads

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 2, 5, 6

  **References**:
  - `scripts/orchestrator.py` — backward compat shim → real logic at `src/oneai_reach/cli/main.py`
  - `src/oneai_reach/cli/main.py` — Click CLI with stages list (line 150-166)
  - `scripts/gmaps_client.py` — created in Task 2, `scrape()` method
  - `scripts/service_detector.py` — created in Task 5, `detect_services()` function
  - `scripts/lead_scorer.py` — created in Task 6, `score_lead()` function
  - `scripts/leads.py` — `load_leads()`, `save_leads()` for DB operations
  - `scripts/config.py` — all pipeline configuration constants

  **Acceptance Criteria**:
  - [ ] `python3 scripts/orchestrator.py "Coffee Shop in Jakarta" --dry-run` works with gosom scraper
  - [ ] New leads from gosom scraper have matched_services and lead_score populated
  - [ ] `python3 scripts/orchestrator.py "Coffee Shop" --scraper-source google-places` still works (fallback)
  - [ ] Existing `--dry-run`, `--followup-only`, `--sync-only` flags unchanged

  **QA Scenarios**:
  ```
  Scenario: Full pipeline dry run with gosom scraper
    Tool: Bash (python3)
    Steps:
      1. python3 scripts/orchestrator.py "Cafe Jakarta" --dry-run --max-leads 5
      2. Check leads in DB for matched_services and lead_score columns
    Expected Result: New leads inserted with matched_services and tier populated
    Evidence: .sisyphus/evidence/task-11-orchestrator-dryrun.txt

  Scenario: Fallback to Google Places works
    Tool: Bash (python3)
    Steps:
      1. python3 scripts/orchestrator.py "Restaurant Jakarta" --scraper-source google-places --dry-run
    Expected Result: Pipeline runs without error (uses existing Google Places scraper)
    Evidence: .sisyphus/evidence/task-11-fallback.txt

  Scenario: Deduplication prevents duplicate leads
    Tool: Bash (python3)
    Steps:
      1. Run orchestrator for same query twice
      2. Count leads in DB
    Expected Result: No duplicate entries (same websiteUri or email filtered)
    Evidence: .sisyphus/evidence/task-11-dedup.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(orchestrator): integrate gosom scraper with service detection pipeline`
  - Files: `scripts/orchestrator.py`, `src/oneai_reach/cli/main.py`

- [x] 12. Add 6 New API Endpoints for Service Views

  **What to do**:
  - Add 6 FastAPI endpoints in `src/oneai_reach/api/v1/`:
    1. `GET /api/v1/agents/services/list` — list all available services with signal counts
    2. `GET /api/v1/agents/funnel/by-service` — funnel breakdown grouped by matched_services
    3. `GET /api/v1/agents/leads/by-tier/{tier}` — leads filtered by tier (hot/warm/cold/skip)
    4. `GET /api/v1/agents/leads/{id}/services` — service detection results for a specific lead
    5. `GET /api/v1/agents/scoring/stats` — scoring distribution across tiers
    6. `GET /api/v1/agents/experiments/status` — A/B test stats across all services
  - Each endpoint queries leads.db using existing repository patterns
  - Return JSON with consistent `{status, message, data}` envelope

  **Must NOT do**:
  - Do NOT modify existing API endpoints
  - Do NOT add authentication (none exists currently)
  - Do NOT use ORM — use existing repository pattern

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 10, 11, 13)
  - **Blocks**: Task 13
  - **Blocked By**: Tasks 5, 6, 4

  **References**:
  - `src/oneai_reach/api/v1/` — existing endpoint files for pattern reference
  - `src/oneai_reach/infrastructure/database/` — repository implementations for DB queries
  - `src/oneai_reach/api/main.py` — FastAPI app setup, router registration
  - `scripts/leads.py` — lead data access patterns
  - `scripts/ab_testing.py` — A/B testing stats (for experiments/status endpoint)

  **Acceptance Criteria**:
  - [ ] `curl -s http://localhost:8001/api/v1/agents/services/list` returns JSON list of services
  - [ ] `curl -s http://localhost:8001/api/v1/agents/funnel/by-service` returns funnel grouped by service
  - [ ] `curl -s http://localhost:8001/api/v1/agents/leads/by-tier/hot` returns hot-tier leads
  - [ ] `curl -s http://localhost:8001/api/v1/agents/scoring/stats` returns tier distribution
  - [ ] Existing endpoints still work (no regressions)

  **QA Scenarios**:
  ```
  Scenario: Services list endpoint returns available services
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8001/api/v1/agents/services/list | python3 -m json.tool
    Expected Result: JSON array with service names and match counts
    Evidence: .sisyphus/evidence/task-12-services-list.txt

  Scenario: Funnel by service groups leads correctly
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8001/api/v1/agents/funnel/by-service | python3 -m json.tool
    Expected Result: JSON with keys being service names, values being stage counts
    Evidence: .sisyphus/evidence/task-12-funnel-service.txt

  Scenario: Tier filter returns only matching leads
    Tool: Bash (curl)
    Steps:
      1. curl -s http://localhost:8001/api/v1/agents/leads/by-tier/hot | python3 -m json.tool
    Expected Result: Only leads with tier='hot' in response
    Evidence: .sisyphus/evidence/task-12-tier-filter.txt

  Scenario: Existing endpoints still work
    Tool: Bash (curl)
    Steps:
      1. curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/agents/leads
    Expected Result: HTTP 200
    Evidence: .sisyphus/evidence/task-12-regression.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(api): add service detection and scoring API endpoints`
  - Files: `src/oneai_reach/api/v1/` new endpoint files

- [x] 13. Update Dashboard Frontend for Service Views

  **What to do**:
  - Add service breakdown section to the Funnel page (`dashboard/src/app/(dashboard)/funnel/page.tsx`)
  - Fetch from new endpoints: `/api/v1/agents/funnel/by-service`, `/api/v1/agents/scoring/stats`
  - Add visual components:
    - Service distribution bar chart (leads per service)
    - Tier distribution donut chart (hot/warm/cold/skip)
    - Service funnel table (stages broken down by service)
  - Add tier filter pills above the leads table (All | Hot | Warm | Cold | Skip)
  - Show matched_services badge on each lead row
  - Use existing shadcn/ui components + recharts (if available) or simple CSS bars

  **Must NOT do**:
  - Do NOT break existing funnel page layout
  - Do NOT add heavy chart libraries — use simple CSS bars or existing deps only
  - Do NOT modify the existing leads table (only ADD tier filter and service badge)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 12)
  - **Blocks**: F3
  - **Blocked By**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/funnel/page.tsx` — current funnel page to extend
  - `dashboard/src/lib/api.ts` — Lead interface and API fetcher
  - `dashboard/package.json` — check if recharts or chart lib already installed
  - `dashboard/src/components/ui/` — existing shadcn/ui components (badge, card, table, etc.)
  - New API endpoints from Task 12: services/list, funnel/by-service, leads/by-tier/{tier}, scoring/stats

  **Acceptance Criteria**:
  - [ ] Dashboard shows service distribution breakdown on funnel page
  - [ ] Tier filter pills work (clicking "Hot" shows only hot-tier leads)
  - [ ] Each lead row shows matched_services as badge(s)
  - [ ] `npm run build` succeeds without errors
  - [ ] Dashboard accessible at reach.aitradepulse.com/funnel with new components

  **QA Scenarios**:
  ```
  Scenario: Service breakdown renders on funnel page
    Tool: Playwright
    Steps:
      1. Navigate to https://reach.aitradepulse.com/funnel
      2. Wait for service breakdown section to render (timeout: 15s)
      3. Screenshot the page
    Expected Result: Page shows service distribution chart/table
    Evidence: .sisyphus/evidence/task-13-service-breakdown.png

  Scenario: Tier filter filters leads correctly
    Tool: Playwright
    Steps:
      1. Navigate to https://reach.aitradepulse.com/funnel
      2. Click the "Hot" tier filter pill
      3. Wait for table to update
      4. Check table rows — all visible leads should be hot tier
    Expected Result: Table shows only hot-tier leads
    Evidence: .sisyphus/evidence/task-13-tier-filter.png

  Scenario: Dashboard builds without errors
    Tool: Bash
    Steps:
      1. cd dashboard && npm run build 2>&1 | tail -5
    Expected Result: Build succeeds with exit code 0
    Evidence: .sisyphus/evidence/task-13-build.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(dashboard): add service breakdown and tier filter to funnel page`
  - Files: `dashboard/src/app/(dashboard)/funnel/page.tsx`, `dashboard/src/lib/api.ts`

- [x] 14. Integration Test — Full Pipeline with 10 Leads

  **What to do**:
  - Run the full pipeline end-to-end with 10 real leads:
    1. `python3 scripts/orchestrator.py "Digital Agency Jakarta" --max-leads 10 --dry-run`
    2. Verify: 10 leads in DB with matched_services, lead_score, tier populated
    3. Verify: Research briefs created in data/research/ with SIGNALS section
    4. Verify: Proposals generated in proposals/drafts/ with service-specific content
    5. Verify: Reviewer scores all proposals (6/10 threshold)
  - Test fallback: stop gosom scraper → run with `--scraper-source google-places` → verify still works
  - Verify brain stores service-specific outcomes
  - Verify dashboard shows the new data

  **Must NOT do**:
  - Do NOT actually send emails or WhatsApp messages (--dry-run only)
  - Do NOT modify any code — this is a verification-only task
  - Do NOT delete test data (leave it for dashboard QA)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (last task, after all others)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 10, 11

  **References**:
  - All modules created in Tasks 1-13
  - `scripts/orchestrator.py` — pipeline entry point
  - `data/leads.db` — verify DB state after pipeline
  - `data/research/` — verify research briefs
  - `proposals/drafts/` — verify proposals
  - Dashboard at `http://localhost:8502/funnel` — verify UI shows data

  **Acceptance Criteria**:
  - [ ] Pipeline completes without errors for 10 leads
  - [ ] All 10 leads have non-NULL matched_services
  - [ ] All 10 leads have non-NULL lead_score and tier
  - [ ] Research briefs contain SIGNALS section
  - [ ] Proposals reference specific services (not generic)
  - [ ] Fallback to Google Places works when gosom is down

  **QA Scenarios**:
  ```
  Scenario: Full pipeline end-to-end with 10 leads
    Tool: Bash (python3)
    Steps:
      1. python3 scripts/orchestrator.py "Digital Agency Jakarta" --max-leads 10 --dry-run 2>&1 | tee /tmp/pipeline-run.log
      2. sqlite3 data/leads.db "SELECT COUNT(*) FROM leads WHERE matched_services IS NOT NULL"
      3. ls data/research/ | wc -l
      4. ls proposals/drafts/ | wc -l
    Expected Result: 10+ leads with services, 10+ research briefs, 10+ proposals
    Evidence: .sisyphus/evidence/task-14-pipeline-e2e.txt

  Scenario: Fallback to Google Places when gosom down
    Tool: Bash
    Steps:
      1. docker stop gmaps-scraper
      2. python3 scripts/orchestrator.py "Restaurant Jakarta" --scraper-source google-places --max-leads 5 --dry-run
      3. docker start gmaps-scraper
    Expected Result: Pipeline completes without error using Google Places fallback
    Evidence: .sisyphus/evidence/task-14-fallback.txt

  Scenario: Brain stores service outcomes
    Tool: Bash (python3)
    Steps:
      1. python3 -c "from scripts.brain_client import search; print(search('website_development Jakarta'))"
    Expected Result: Returns relevant stored outcome data
    Evidence: .sisyphus/evidence/task-14-brain-outcomes.txt

  Scenario: Dashboard shows new data
    Tool: Playwright
    Steps:
      1. Navigate to https://reach.aitradepulse.com/funnel
      2. Verify tier filter pills visible
      3. Verify leads table has data
      4. Screenshot
    Expected Result: Dashboard renders with service data
    Evidence: .sisyphus/evidence/task-14-dashboard.png
  ```

  **Commit**: NO (verification-only task, no code changes)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run linter + type checks on all new/modified Python files. Check for: `as any` patterns, empty catches, console.log in prod, hardcoded URLs/keys, unused imports. Verify config.py used for all settings. Verify no port conflicts (8000, 3000, 8502, 8001 not reused).
  Output: `Lint [PASS/FAIL] | Type Check [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **End-to-End QA** — `unspecified-high`
  Run full pipeline: scrape 10 leads → detect services → score → generate proposals → review → verify service-specific content. Check: (1) scraper returns data, (2) each lead has matched_services, (3) each lead has tier, (4) proposals reference correct service, (5) brain stores service in outcome, (6) dashboard /api/v1/agents/funnel/by-service returns data.
  Save evidence to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Verify leads.db only had columns ADDED, not changed. Verify Google Places API still works as fallback.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(scraper): add gosom scraper Docker deployment and Python client` — gmaps_client.py, gmaps-scraper.service, templates/*.yaml, schema migration
- **Wave 2**: `feat(detection): add service detector, lead scorer, signal detection` — service_detector.py, lead_scorer.py, researcher enhancements, brain_client updates
- **Wave 3**: `feat(pipeline): multi-service proposal generation and dashboard` — generator updates, orchestrator updates, API endpoints, dashboard changes
- Pre-commit: `python3 -m py_compile scripts/*.py` on all changed files

---

## Success Criteria

### Verification Commands
```bash
# Scraper running
curl -s http://localhost:8082/api/v1/jobs | python3 -m json.tool

# Service detection works
python3 -c "from scripts.service_detector import detect_services; print(detect_services({'websiteUri': '', 'reviewCount': 150, 'primaryType': 'restaurant'}, {}))"

# Lead scoring works
python3 -c "from scripts.lead_scorer import score_lead; print(score_lead({'websiteUri': '', 'reviewCount': 150}, {}))"

# Templates parse correctly
python3 -c "import yaml; [yaml.safe_load(open(f'templates/{t}')) for t in ['website_development.yaml','adforge_ai.yaml','ai_agent_pro.yaml','social_media_management.yaml','ai_automation.yaml']]"

# Brain client service query
python3 -c "from scripts.brain_client import get_strategy; print(get_strategy('restaurant', 'Jakarta', service='website_development'))"

# API endpoints exist
curl -s http://localhost:8001/api/v1/agents/services/list | python3 -m json.tool
curl -s http://localhost:8001/api/v1/agents/funnel/by-service | python3 -m json.tool
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] gosom scraper returns real business data
- [ ] Service detector returns ranked services for sample leads
- [ ] Proposals are service-specific (not generic)
- [ ] Brain client stores and retrieves service-specific outcomes
- [ ] Dashboard shows service breakdown
- [ ] Existing pipeline still works end-to-end
- [ ] No port conflicts with existing services
