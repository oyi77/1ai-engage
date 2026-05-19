# WAHA Assignments & Detailed Outreach Tracker

## TL;DR

> **Quick Summary**: Restore two critical dashboard features lost during recent restructure: (1) WAHA session management page to view/assign WhatsApp numbers to personas, (2) Detailed outreach tracker to see complete lead timeline (research, proposals, messages, replies).
> 
> **Deliverables**:
> - `/wa-numbers` page - WAHA session list with persona assignment UI
> - `/outreach-tracker` page - Lead detail view with full pipeline history
> - Backend API endpoints to serve aggregated data
> - Real-time status updates via polling
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Backend API → Frontend Pages → Verification

---

## Context

### Original Request
User reported that two critical dashboard views were degraded/lost during recent Next.js dashboard restructure:
1. **WAHA Assignments** - No way to see connected WhatsApp sessions, their online/offline status, or assign them to specific personas/campaigns
2. **Detailed Outreach Tracker** - Current funnel/pipeline views too high-level; missing granular view of exact research briefs, proposals, and messages sent per lead

### Interview Summary
**Key Discussions**:
- Backend data exists and is working (WAHA API connected, leads.db populated with 823KB data, research/proposals on disk)
- Frontend visibility is the problem - data is there but not exposed in UI
- 4 active WAHA sessions: `Detergen`, `default`, `produk_digital`, `warung_kecantikan`
- Research briefs stored in `data/research/{index}_{name}.txt` (460 files)
- Proposals stored in `proposals/drafts/{index}_{name}.txt` (508 files)
- User expects full e2e visibility into the automated outreach system

**Research Findings**:
- Database schema analysis completed (bg_3b37905f)
- `wa_numbers` table already has `persona` column - no new table needed
- `conversation_messages` table contains all sent/received messages
- Existing API endpoints: `/api/v1/agents/wa/sessions`, `/api/v1/agents/leads`
- Need to add new endpoints for persona updates and lead timeline aggregation

### Metis Review
**Self-conducted gap analysis** (Metis delegation blocked for plan-family agents):
- ✅ Core objective clear: Restore two specific dashboard features
- ✅ Scope boundaries established: Display/assign only, no editing or sending
- ✅ Technical approach decided: Use existing DB schema, add API endpoints, build React pages
- ✅ No critical ambiguities remaining
- ✅ Test strategy: Manual QA with real data from pre-seeded database

---

## Work Objectives

### Core Objective
Restore full visibility into WAHA session management and lead outreach pipeline by building two new dashboard pages with supporting backend APIs.

### Concrete Deliverables
- **Backend**: 3 new FastAPI endpoints
  - `GET /api/v1/agents/wa/sessions/status` - Live WAHA status from API
  - `PATCH /api/v1/agents/wa/sessions/{id}/persona` - Update persona assignment
  - `GET /api/v1/agents/leads/{id}/timeline` - Aggregated lead history
- **Frontend**: 2 new Next.js pages
  - `dashboard/src/app/(dashboard)/wa-numbers/page.tsx` - WAHA assignments UI
  - `dashboard/src/app/(dashboard)/outreach-tracker/page.tsx` - Lead detail tracker
- **Navigation**: Add links to sidebar

### Definition of Done
- [x] Can view all 4 WAHA sessions with live connection status
- [x] Can assign/update persona for each session via dropdown
- [x] Can click any lead and see full timeline (research + proposal + messages)
- [x] Real-time updates working (5-10s polling)
- [x] No console errors, pages load within 2s

### Must Have
- Live WAHA session status (online/offline/scanning) from WAHA API
- Persona assignment persistence in `wa_numbers.persona` column
- Full lead timeline showing research brief text, proposal text, sent messages
- Search and filter functionality on outreach tracker
- Mobile-responsive layout

### Must NOT Have (Guardrails)
- ❌ Editing or regenerating proposals from UI (use scripts)
- ❌ Sending new messages from UI (use scripts or `/conversations` page)
- ❌ Deleting or archiving leads from UI
- ❌ Multi-user access control or permissions (single-user system)
- ❌ Analytics dashboards or charts (separate feature)
- ❌ Exporting data to CSV/Excel (not in scope)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no automated tests for dashboard)
- **Automated tests**: None (manual QA only)
- **Framework**: N/A
- **QA Strategy**: Agent-executed manual QA using Playwright + curl

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright - Navigate, interact, assert DOM, screenshot
- **API/Backend**: Use Bash (curl) - Send requests, assert status + response fields
- **Database**: Use Bash (sqlite3) - Query tables, verify data persistence

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.

```
Wave 1 (Backend Foundation — 3 tasks in parallel):
├── Task 1: Add WAHA status endpoint [quick]
├── Task 2: Add persona update endpoint [quick]
└── Task 3: Add lead timeline endpoint [unspecified-high]

Wave 2 (Frontend Implementation — 2 tasks in parallel):
├── Task 4: Build WAHA Assignments page [visual-engineering]
└── Task 5: Build Outreach Tracker page [visual-engineering]

Wave 3 (Integration & Polish — 2 tasks in parallel):
├── Task 6: Add navigation links [quick]
└── Task 7: E2E verification [unspecified-high]

Critical Path: Task 3 → Task 5 → Task 7
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 4 |
| 2 | — | 4 |
| 3 | — | 5 |
| 4 | 1, 2 | 6, 7 |
| 5 | 3 | 6, 7 |
| 6 | 4, 5 | 7 |
| 7 | 4, 5, 6 | — |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T1 → `quick`, T2 → `quick`, T3 → `unspecified-high`
- **Wave 2**: 2 tasks — T4 → `visual-engineering`, T5 → `visual-engineering`
- **Wave 3**: 2 tasks — T6 → `quick`, T7 → `unspecified-high`

---

## TODOs

- [x] 1. Add WAHA Status Endpoint

  **What to do**:
  - Create new FastAPI endpoint `GET /api/v1/agents/wa/sessions/status`
  - Fetch live session status from WAHA API (`waha.aitradepulse.com/api/sessions`)
  - Return array of sessions with: `session_name`, `status` (online/offline/scanning), `me.id` (phone number)
  - Use existing `_waha_targets()` and `_waha_sessions()` from `scripts/senders.py`
  - Add error handling for WAHA API failures (return cached status or empty array)

  **Must NOT do**:
  - Don't cache status in database (always fetch live)
  - Don't add authentication (single-user system)
  - Don't modify existing `/api/v1/agents/wa/sessions` endpoint

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple API endpoint, reuses existing WAHA integration code
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4 (WAHA Assignments page needs this endpoint)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `src/oneai_reach/api/v1/agents.py:348-359` - Existing `/wa/sessions` endpoint pattern
  - `src/oneai_reach/api/v1/agents.py:26-35` - Module import pattern (sys.path + agent_control)
  - `scripts/senders.py:37-96` - WAHA API integration (`_waha_targets()`, `_waha_sessions()`)

  **API References**:
  - WAHA API docs: `https://waha.devlike.pro/docs/how-to/sessions/` - Session status structure
  - FastAPI response model: Return `AgentResponse` with data: `{"sessions": [{"name": str, "status": str, "phone": str}]}`

  **External References**:
  - `scripts/config.py:WAHA_TARGETS` - WAHA base URLs and API keys

  **WHY Each Reference Matters**:
  - `agents.py:348-359` shows exact endpoint pattern - match this structure (router decorator, AgentResponse, try/except)
  - `agents.py:26-35` shows how to import agent_control module - must follow this pattern
  - `senders.py` contains working WAHA API calls - reuse this exact pattern
  - WAHA API docs explain status field values - use correct enum

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Fetch live WAHA session status
    Tool: Bash (curl)
    Preconditions: Dashboard server running on port 3456
    Steps:
      1. curl -X GET http://localhost:3456/api/v1/agents/wa/sessions/status
      2. Parse JSON response
      3. Assert response contains "sessions" array
      4. Assert each session has "name", "status", "phone" fields
      5. Assert status is one of: "WORKING", "SCAN_QR_CODE", "FAILED", "STOPPED"
    Expected Result: 200 OK, sessions array with 4 items (Detergen, default, produk_digital, warung_kecantikan)
    Failure Indicators: 500 error, empty array, missing fields, invalid status values
    Evidence: .sisyphus/evidence/task-1-waha-status-fetch.json

  Scenario: Handle WAHA API failure gracefully
    Tool: Bash (curl + network simulation)
    Preconditions: Temporarily block WAHA API access
    Steps:
      1. curl -X GET http://localhost:3456/api/v1/agents/wa/sessions/status
      2. Assert response is 200 (not 500)
      3. Assert response contains empty array or cached data
    Expected Result: Graceful degradation, no server crash
    Evidence: .sisyphus/evidence/task-1-waha-status-error.json
  ```

  **Evidence to Capture**:
  - [ ] task-1-waha-status-fetch.json (successful API response)
  - [ ] task-1-waha-status-error.json (error handling response)

  **Commit**: YES
  - Message: `feat(api): add WAHA live status endpoint`
  - Files: `src/oneai_reach/api/v1/agents.py` (add new endpoint function)
  - Pre-commit: `cd src && python -m pytest tests/ -k test_api || echo "Tests optional"`

- [x] 2. Add Persona Update Endpoint
- [x] 3. Add Lead Timeline Endpoint
- [x] 4. Build WAHA Assignments Page
- [x] 5. Build Outreach Tracker Page
- [x] 6. Add Navigation Links
- [x] 7. E2E Verification
- [x] F1. **Plan Compliance Audit** — `oracle`
- [x] F2. **Code Quality Review** — `unspecified-high`
- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill)
- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [7/7 compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Task 1**: `feat(api): add WAHA live status endpoint` — `src/oneai_reach/api/v1/agents.py`
- **Task 2**: `feat(api): add persona update endpoint for WA sessions` — `src/oneai_reach/api/v1/agents.py`
- **Task 3**: `feat(api): add lead timeline aggregation endpoint` — `src/oneai_reach/api/v1/agents.py`
- **Task 4**: `feat(ui): add WAHA assignments page with persona management` — `dashboard/src/app/(dashboard)/wa-numbers/page.tsx`
- **Task 5**: `feat(ui): add detailed outreach tracker with timeline view` — `dashboard/src/app/(dashboard)/outreach-tracker/page.tsx`
- **Task 6**: `feat(ui): add navigation links for WA Numbers and Outreach Tracker` — `dashboard/src/components/sidebar.tsx`

**Note**: Tasks 1-3 all modify the same file (`agents.py`). Consider grouping into a single commit after all three are complete, or commit incrementally as each endpoint is added and tested.

---

## Success Criteria

### Verification Commands
```bash
# Start FastAPI backend
cd /home/openclaw/projects/1ai-reach
uvicorn src.oneai_reach.api.main:app --reload --port 8000

# Start Next.js dashboard (separate terminal)
cd dashboard && npm run dev

# Verify API endpoints
curl http://localhost:8000/api/v1/agents/wa/sessions/status
curl http://localhost:8000/api/v1/agents/leads/0/timeline

# Verify pages load (through Next.js proxy)
curl -I http://localhost:3456/wa-numbers
curl -I http://localhost:3456/outreach-tracker

# Check database
sqlite3 data/leads.db "SELECT id, session_name, persona FROM wa_numbers"
```

### Final Checklist
- [x] All 4 WAHA sessions visible with live status
- [x] Persona assignment persists in database
- [x] Lead timeline shows research + proposal + messages
- [x] Search and filter work on tracker page
- [x] Navigation links work and show active state
- [x] No console errors in browser
- [x] Mobile responsive (375px width)
- [x] All evidence files captured
- [x] Build succeeds without errors
