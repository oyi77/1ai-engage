# Phase B: CRM Foundations — WhatsApp CRM

## TL;DR

> **Quick Summary**: Transform the conversation room into a full CRM with contact profiles, proposals management, email tracking, and WAHA labels sync.
> 
> **Deliverables**:
> - Contact profile panel (view/edit contact details, history, tags)
> - Proposals page (create, view, track proposals per contact)
> - Email tracking in conversations (sent, delivered, opened, clicked)
> - WAHA labels sync in dashboard (create, assign, filter by labels)
> - Contact merge/deduplicate UI
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 (DB schema) → Task 2 (contact profile API) → Task 3 (proposals API) → Task 4 (email tracking) → Task 5 (labels sync) → Task 6-9 (UI) → Task 10 (integration) → Task 11 (QA)

---

## Context

### Original Request
User identified missing features after Phase A completion:
- "没有建议页面来管理建议、审查、提供反馈、显示哪些建议具有高转化率等" → Phase B
- "没有电子邮件跟踪→已发送电子邮件、已回复电子邮件等" → Phase B

### Phase Progression
- **Phase A** ✅: Conversation Essentials (history, media, presence, templates, tags)
- **Phase B** 🔄: CRM Foundations (contact profile, proposals, email tracking, labels)
- **Phase C** 📋: Full Pipeline (email composer, templates, scheduled messages, broadcast, analytics)

### Interview Summary
**Key Discussions**:
- Proposals page: Should show all proposals for a contact, with status (draft, sent, accepted, rejected)
- Email tracking: Should show in conversation view when email was sent, opened, clicked
- Contact profile: Should show all contact details, conversation history, tags, proposals
- WAHA labels: Should sync with dashboard, allow creating/assigning/filtering

**Research Findings**:
- WAHA Labels API: `GET/POST/PUT/DELETE /api/:session/labels` with name + color
- WAHA Label Assignment: `POST /api/:session/labels/{label_id}/chats` to assign label to chat
- Email tracking already exists in `email_events` table (delivery, open, click, bounce)
- Proposals stored in `proposals/` directory and `leads` table

---

## Work Objectives

### Core Objective
Transform the conversation room from a chat viewer into a full CRM with contact management, proposals tracking, email visibility, and label organization.

### Concrete Deliverables
- `GET /api/v1/contacts/{id}` — full contact profile with history
- `PUT /api/v1/contacts/{id}` — update contact details
- `GET /api/v1/contacts/{id}/proposals` — list proposals for contact
- `POST /api/v1/contacts/{id}/proposals` — create proposal for contact
- `GET /api/v1/conversations/{id}/emails` — email events for conversation
- `GET/POST/DELETE /api/v1/waha/{session}/labels/{label_id}/chats` — label assignment
- Dashboard: Contact profile panel, proposals tab, email tracking panel, labels filter

### Definition of Done
- [ ] Can view contact profile with all details, history, tags, proposals
- [ ] Can edit contact name, email, phone, company, notes
- [ ] Can create/view/track proposals per contact
- [ ] Can see email events (sent, delivered, opened, clicked) in conversation
- [ ] Can create WAHA labels and assign to conversations
- [ ] Can filter conversation list by label

### Must Have
- Contact profile panel with edit capability
- Proposals list with status tracking
- Email events display in conversation
- WAHA labels sync (create, assign, filter)

### Must NOT Have (Guardrails)
- NO Full email composer (Phase C)
- NO Email templates (Phase C)
- NO Advanced analytics (Phase C)
- NO Bulk operations (Phase C)
- NO Mobile-responsive redesign

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: None (tests-after if needed)
- **Framework**: Playwright for UI, curl for API

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (DB Schema):
└── Task 1: DB schema migrations [quick]

Wave 1 (Backend APIs — after schema):
├── Task 2: Contact profile API (GET/PUT /contacts/{id}) [unspecified-high]
├── Task 3: Proposals API (GET/POST /contacts/{id}/proposals) [unspecified-high]
├── Task 4: Email tracking API (GET /conversations/{id}/emails) [quick]
└── Task 5: WAHA labels sync API (CRUD + assign) [unspecified-high]

Wave 2 (Dashboard UI — after APIs):
├── Task 6: Contact profile panel component [visual-engineering]
├── Task 7: Proposals tab component [visual-engineering]
├── Task 8: Email tracking panel component [visual-engineering]
└── Task 9: Labels filter component [visual-engineering]

Wave 3 (Integration + QA):
├── Task 10: Conversation page integration [visual-engineering]
└── Task 11: E2E QA with Playwright [deep]

Wave FINAL:
├── Task F1: Plan compliance audit [deep]
├── Task F2: Code quality review [unspecified-high]
└── Task F3: Real manual QA [unspecified-high]
```

### Agent Dispatch Summary
- **Wave 0**: T1→`quick`
- **Wave 1**: T2-T3→`unspecified-high`, T4→`quick`, T5→`unspecified-high`
- **Wave 2**: T6-T9→`visual-engineering`
- **Wave 3**: T10→`visual-engineering`, T11→`deep`
- **FINAL**: F1→`deep`, F2-F3→`unspecified-high`

---

## TODOs

- [ ] 1. **DB Schema Migrations** (proposals table)

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/migration_crm_phase_b.py`
  - Add `proposals` table:
    ```sql
    CREATE TABLE IF NOT EXISTS proposals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      wa_number_id TEXT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'sent', 'accepted', 'rejected')),
      sent_at TEXT,
      accepted_at TEXT,
      rejected_at TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
      FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL
    );
    CREATE INDEX IF NOT EXISTS idx_proposals_contact ON proposals(contact_id);
    CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
    CREATE INDEX IF NOT EXISTS idx_proposals_wa ON proposals(wa_number_id);
    ```
  - Add `email_events` table (if not exists):
    ```sql
    CREATE TABLE IF NOT EXISTS email_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER,
      conversation_id INTEGER,
      email TEXT NOT NULL,
      event_type TEXT NOT NULL CHECK(event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')),
      metadata TEXT DEFAULT '{}',
      timestamp TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
      FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
    );
    CREATE INDEX IF NOT EXISTS idx_email_events_contact ON email_events(contact_id);
    CREATE INDEX IF NOT EXISTS idx_email_events_conv ON email_events(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_email_events_type ON email_events(event_type);
    ```
  - Register migration in `main.py` (after CRM Phase A migration)
  - Run migration, verify tables exist

  **Must NOT do**: Don't modify existing tables. Only ADD new tables.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocks**: Tasks 2, 3, 4

  **References**:
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py` — Phase A migration pattern
  - `src/oneai_reach/api/main.py` — migration registration

  **Why**: Proposals and email_events tables are needed before API endpoints can be built. Following the same migration pattern as Phase A ensures consistency.

  **Acceptance Criteria**:
  - [ ] `proposals` table created with correct schema
  - [ ] `email_events` table created with correct schema
  - [ ] Indexes created for performance
  - [ ] Migration registered in `main.py`

  **QA Scenarios**:
  ```
  Scenario: Migration creates tables
    Tool: Bash (sqlite3)
    Steps:
      1. python3 -c "from oneai_reach.infrastructure.database.migration_crm_phase_b import run_phase_b_migration; run_phase_b_migration('data/leads.db')"
      2. sqlite3 data/leads.db ".tables"
    Expected Result: Output includes proposals, email_events
    Evidence: .sisyphus/evidence/task-1-tables.txt
  ```

  **Commit**: YES
  - Message: `feat(crm): add Phase B DB schema — proposals and email_events tables`
  - Files: `src/oneai_reach/infrastructure/database/migration_crm_phase_b.py`, `src/oneai_reach/api/main.py`

- [ ] 2. **Contact Profile API** (GET/PUT /contacts/{id})

  **What to do**:
  - Create `src/oneai_reach/api/v1/contact_profile.py` with router
  - Implement:
    - `GET /api/v1/contacts/{id}` — full contact profile with:
      - Contact details: `{ id, name, email, phone, company, notes, tags, source, created_at, updated_at }`
      - Conversation history: `[{ id, wa_number_id, contact_phone, status, last_message_at, message_count }]`
      - Proposals list: `[{ id, title, status, created_at }]`
      - Email events: `[{ id, event_type, email, timestamp }]`
    - `PUT /api/v1/contacts/{id}` — update contact details
      - Body: `{ name?, email?, phone?, company?, notes?, tags? }`
      - Returns: `{ status: "success", data: { contact: {...} } }`
    - `GET /api/v1/contacts/{id}/history` — conversation history with pagination
      - Query params: `?limit=10&offset=0`
      - Returns: `{ status: "success", data: { conversations: [...], total: N } }`
  - Use existing `contacts` table, `conversations` table, `proposals` table, `email_events` table
  - Register router in `main.py`

  **Must NOT do**: Don't duplicate existing contact endpoints. Extend them.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 6 (contact profile UI)

  **References**:
  - `src/oneai_reach/api/v1/contacts.py` — existing contact endpoints (lines 1-50 for pattern)
  - `scripts/state_manager.py` — conversations and messages tables
  - `src/oneai_reach/api/v1/conversations.py` — conversation endpoints pattern

  **Why**: The contact profile API aggregates data from multiple tables (contacts, conversations, proposals, email_events) into a single response for the UI. This avoids multiple API calls from the frontend.

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/contacts/1` returns full profile with history, proposals, emails
  - [ ] `PUT /api/v1/contacts/1` updates contact details
  - [ ] `GET /api/v1/contacts/1/history?limit=10` returns conversation history
  - [ ] 404 returned for non-existent contact

  **QA Scenarios**:
  ```
  Scenario: Get contact profile
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/contacts/1
    Expected Result: 200 OK with contact details, history, proposals, emails
    Evidence: .sisyphus/evidence/task-2-contact-profile.json

  Scenario: Update contact
    Tool: Bash (curl)
    Steps:
      1. curl -s -X PUT http://127.0.0.1:8001/api/v1/contacts/1 -H "Content-Type: application/json" -d '{"company":"Acme Corp","notes":"VIP customer"}'
    Expected Result: 200 OK with updated contact
    Evidence: .sisyphus/evidence/task-2-contact-update.json

  Scenario: Contact not found
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/contacts/99999
    Expected Result: 404 Not Found
    Evidence: .sisyphus/evidence/task-2-contact-404.txt
  ```

  **Commit**: YES
  - Message: `feat(crm): add contact profile API with history, proposals, emails`
  - Files: `src/oneai_reach/api/v1/contact_profile.py`, `src/oneai_reach/api/main.py`

- [ ] 3. **Proposals API** (GET/POST /contacts/{id}/proposals)

  **What to do**:
  - Create `src/oneai_reach/api/v1/proposals.py` with router
  - Implement:
    - `GET /api/v1/contacts/{id}/proposals` — list proposals for contact
      - Returns: `{ status: "success", data: { proposals: [{ id, title, content, status, sent_at, created_at }] } }`
    - `POST /api/v1/contacts/{id}/proposals` — create proposal
      - Body: `{ title: string, content: string, wa_number_id?: string }`
      - Returns: `{ status: "success", data: { id, title, content, status: "draft" } }`
    - `GET /api/v1/proposals/{id}` — get proposal details
      - Returns: `{ status: "success", data: { id, contact_id, title, content, status, sent_at, created_at } }`
    - `PUT /api/v1/proposals/{id}` — update proposal
      - Body: `{ title?, content?, status? }`
      - Status transitions: draft → sent → accepted/rejected
      - Returns: `{ status: "success", data: { id, title, content, status } }`
    - `DELETE /api/v1/proposals/{id}` — delete proposal
      - Returns: `{ status: "success", data: { deleted: id } }`
  - Register router in `main.py`

  **Must NOT do**: Don't build proposal generator. Just CRUD.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 7 (proposals UI)

  **References**:
  - `src/oneai_reach/api/v1/templates.py` — CRUD endpoint pattern
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_b.py` — proposals table schema

  **Why**: Proposals are a core CRM feature. The API follows the same CRUD pattern as templates for consistency.

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/contacts/1/proposals` returns list of proposals
  - [ ] `POST /api/v1/contacts/1/proposals` creates new proposal with status "draft"
  - [ ] `PUT /api/v1/proposals/1` updates proposal status
  - [ ] `DELETE /api/v1/proposals/1` deletes proposal
  - [ ] 404 returned for non-existent proposal

  **QA Scenarios**:
  ```
  Scenario: Create proposal
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/contacts/1/proposals -H "Content-Type: application/json" -d '{"title":"Website Redesign","content":"We propose a complete website redesign..."}'
    Expected Result: 200 OK with proposal id and status "draft"
    Evidence: .sisyphus/evidence/task-3-proposal-create.json

  Scenario: List proposals
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/contacts/1/proposals
    Expected Result: 200 OK with proposals array
    Evidence: .sisyphus/evidence/task-3-proposal-list.json

  Scenario: Update proposal status
    Tool: Bash (curl)
    Steps:
      1. curl -s -X PUT http://127.0.0.1:8001/api/v1/proposals/1 -H "Content-Type: application/json" -d '{"status":"sent"}'
    Expected Result: 200 OK with updated status
    Evidence: .sisyphus/evidence/task-3-proposal-update.json

  Scenario: Delete proposal
    Tool: Bash (curl)
    Steps:
      1. curl -s -X DELETE http://127.0.0.1:8001/api/v1/proposals/1
    Expected Result: 200 OK with deleted id
    Evidence: .sisyphus/evidence/task-3-proposal-delete.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add proposals CRUD API`
  - Files: `src/oneai_reach/api/v1/proposals.py`, `src/oneai_reach/api/main.py`

- [ ] 4. **Email Tracking API** (GET /conversations/{id}/emails)

  **What to do**:
  - Create `GET /api/v1/conversations/{id}/emails` endpoint in `conversations.py`
  - Query `email_events` table for events related to conversation's contact email
  - Return events with type, timestamp, metadata
  - Response format:
    ```json
    {
      "status": "success",
      "data": {
        "events": [
          {
            "id": 1,
            "event_type": "sent",
            "email": "contact@example.com",
            "subject": "Proposal",
            "timestamp": "2026-04-25T10:00:00",
            "metadata": "{}"
          }
        ],
        "count": 5
      }
    }
    ```
  - Add to existing `conversations.py` (don't create new file)

  **Must NOT do**: Don't build email sending. Just display tracking.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 8 (email tracking UI)

  **References**:
  - `src/oneai_reach/api/v1/conversations.py` — existing conversation endpoints
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_b.py` — email_events table schema

  **Why**: Email tracking data already exists in the system. This endpoint just exposes it through the conversation API for the UI.

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/conversations/1/emails` returns email events for contact
  - [ ] Events sorted by timestamp descending (newest first)
  - [ ] Empty array returned if no events

  **QA Scenarios**:
  ```
  Scenario: Get email events
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/conversations/1/emails
    Expected Result: 200 OK with email events array
    Evidence: .sisyphus/evidence/task-4-emails.json

  Scenario: No email events
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/conversations/999/emails
    Expected Result: 200 OK with empty events array
    Evidence: .sisyphus/evidence/task-4-emails-empty.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add email tracking API endpoint`
  - Files: `src/oneai_reach/api/v1/conversations.py`

- [ ] 5. **WAHA Labels Sync API** (CRUD + assign)

  **What to do**:
  - Extend `src/oneai_reach/api/v1/waha_proxy.py` with label assignment:
    - `POST /api/v1/waha/{session}/labels/{label_id}/chats` — assign label to chat
      - Body: `{ chatId: "6281234567890@c.us" }`
      - Proxies to WAHA: `POST /api/{session}/labels/{label_id}/chats`
    - `DELETE /api/v1/waha/{session}/labels/{label_id}/chats/{chat_id}` — remove label from chat
      - Proxies to WAHA: `DELETE /api/{session}/labels/{label_id}/chats/{chat_id}`
    - `GET /api/v1/waha/{session}/labels/{label_id}/chats` — list chats with label
      - Proxies to WAHA: `GET /api/{session}/labels/{label_id}/chats`
  - Add `GET /api/v1/conversations/labels` — list all labels across sessions
    - Returns: `{ status: "success", data: { labels: [{ id, name, color, session }] } }`
  - Add label filter to conversations list: `GET /api/v1/conversations?label_id=X`
    - Filters conversations that have the specified label assigned

  **Must NOT do**: Don't auto-sync DB tags to WAHA labels. They're separate systems.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 9 (labels filter UI)

  **References**:
  - `src/oneai_reach/api/v1/waha_proxy.py` — existing WAHA proxy (lines 1-50 for pattern)
  - WAHA source: `/home/openclaw/projects/waha/src/api/labels.controller.ts` — labels CRUD

  **Why**: WAHA labels sync with the WhatsApp phone app. Users can create labels on their phone and see them in the dashboard, and vice versa.

  **Acceptance Criteria**:
  - [ ] `POST /api/v1/waha/warung_kecantikan/labels/1/chats` assigns label to chat
  - [ ] `DELETE /api/v1/waha/warung_kecantikan/labels/1/chats/6281234567890@c.us` removes label
  - [ ] `GET /api/v1/conversations/labels` returns all labels across sessions
  - [ ] `GET /api/v1/conversations?label_id=1` filters by label

  **QA Scenarios**:
  ```
  Scenario: Assign label to chat
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/waha/warung_kecantikan/labels/1/chats -H "Content-Type: application/json" -d '{"chatId":"6281234567890@c.us"}'
    Expected Result: 200 OK
    Evidence: .sisyphus/evidence/task-5-label-assign.json

  Scenario: List all labels
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/conversations/labels
    Expected Result: 200 OK with labels array
    Evidence: .sisyphus/evidence/task-5-labels-list.json

  Scenario: Filter conversations by label
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://127.0.0.1:8001/api/v1/conversations?label_id=1"
    Expected Result: 200 OK with filtered conversations
    Evidence: .sisyphus/evidence/task-5-label-filter.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add WAHA labels sync API with assignment and filtering`
  - Files: `src/oneai_reach/api/v1/waha_proxy.py`, `src/oneai_reach/api/v1/conversations.py`

- [ ] 6. **Contact Profile Panel Component** (Dashboard UI)

  **What to do**:
  - Create contact profile panel that slides in when clicking a contact name in conversation header
  - Use `Sheet` component from `dashboard/src/components/ui/sheet.tsx`
  - Show:
    - Contact name (editable)
    - Email (editable)
    - Phone (read-only)
    - Company (editable)
    - Notes (editable textarea)
    - Tags (add/remove)
    - Created date
  - Tabs: History, Proposals, Emails
  - History tab: list of conversations with status and last message
  - Proposals tab: list of proposals with status badges (see Task 7)
  - Emails tab: email events timeline (see Task 8)
  - Edit mode: click "Edit" button to enable inline editing, "Save" to persist
  - API calls:
    - `GET /api/v1/contacts/{id}` on panel open
    - `PUT /api/v1/contacts/{id}` on save
    - `GET /api/v1/contacts/{id}/proposals` on Proposals tab click
    - `GET /api/v1/conversations/{id}/emails` on Emails tab click

  **Must NOT do**: Don't redesign the page. Add a side panel.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 10 (integration)

  **References**:
  - `dashboard/src/components/ui/sheet.tsx` — slide-in panel component
  - `dashboard/src/components/ui/tabs.tsx` — tabs component
  - `dashboard/src/app/(dashboard)/contacts/page.tsx` — existing contacts page for pattern
  - `dashboard/src/lib/api.ts` — API functions

  **Why**: The contact profile panel aggregates all contact information in one place, making it easy for users to view and edit contact details without leaving the conversation page.

  **Acceptance Criteria**:
  - [ ] Clicking contact name in conversation header opens profile panel
  - [ ] Panel shows all contact details
  - [ ] Can edit name, email, company, notes inline
  - [ ] Tabs show history, proposals, emails
  - [ ] Panel closes when clicking outside or X button

  **QA Scenarios**:
  ```
  Scenario: Open contact profile
    Tool: Playwright
    Steps:
      1. Open conversations page
      2. Click on a conversation
      3. Click on contact name in header
    Expected Result: Profile panel slides in with contact details
    Evidence: .sisyphus/evidence/task-6-contact-profile.png

  Scenario: Edit contact
    Tool: Playwright
    Steps:
      1. Open contact profile
      2. Click "Edit" button
      3. Change company name
      4. Click "Save"
    Expected Result: Contact updated, success message shown
    Evidence: .sisyphus/evidence/task-6-contact-edit.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add contact profile panel component`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 7. **Proposals Tab Component** (Dashboard UI)

  **What to do**:
  - Create proposals tab in contact profile panel
  - List proposals with status badges:
    - draft = gray badge
    - sent = blue badge
    - accepted = green badge
    - rejected = red badge
  - Each proposal shows: title, status badge, created date
  - Click to expand and view proposal content
  - "New Proposal" button opens dialog with:
    - Title input
    - Content textarea
    - Save button
  - Status update buttons:
    - draft → "Mark as Sent"
    - sent → "Mark as Accepted" / "Mark as Rejected"
  - API calls:
    - `GET /api/v1/contacts/{id}/proposals` on tab click
    - `POST /api/v1/contacts/{id}/proposals` on create
    - `PUT /api/v1/proposals/{id}` on status update

  **Must NOT do**: Don't build proposal generator. Just CRUD UI.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 10 (integration)

  **References**:
  - `dashboard/src/components/ui/dialog.tsx` — modal component
  - `dashboard/src/components/ui/badge.tsx` — badge component
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing pattern

  **Why**: Proposals are a core CRM feature. The tab provides quick access to create and track proposals without leaving the conversation.

  **Acceptance Criteria**:
  - [ ] Proposals tab shows list of proposals with status badges
  - [ ] Can create new proposal via dialog
  - [ ] Can update proposal status
  - [ ] Can expand to view proposal content

  **QA Scenarios**:
  ```
  Scenario: Create proposal
    Tool: Playwright
    Steps:
      1. Open contact profile
      2. Click Proposals tab
      3. Click "New Proposal"
      4. Fill in title and content
      5. Click Save
    Expected Result: Proposal appears in list with "draft" status
    Evidence: .sisyphus/evidence/task-7-proposal-create.png

  Scenario: Update proposal status
    Tool: Playwright
    Steps:
      1. Open Proposals tab
      2. Click "Mark as Sent" on a draft proposal
    Expected Result: Status changes to "sent" with blue badge
    Evidence: .sisyphus/evidence/task-7-proposal-status.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add proposals tab component`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 8. **Email Tracking Panel Component** (Dashboard UI)

  **What to do**:
  - Create emails tab in contact profile panel
  - Show email events timeline:
    - Each event shows: event_type badge, email address, subject, timestamp
    - Event types with colors:
      - sent = blue
      - delivered = green
      - opened = yellow
      - clicked = purple
      - bounced = red
      - complained = red
    - Timeline sorted by timestamp descending (newest first)
  - Empty state: "No email events yet" message
  - API calls:
    - `GET /api/v1/conversations/{id}/emails` on tab click

  **Must NOT do**: Don't build email composer. Just display tracking.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 10 (integration)

  **References**:
  - `dashboard/src/components/ui/badge.tsx` — badge component
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing pattern

  **Why**: Email tracking visibility helps users understand the engagement level of their contacts and follow up at the right time.

  **Acceptance Criteria**:
  - [ ] Emails tab shows email events timeline
  - [ ] Event types are color-coded
  - [ ] Empty state shown when no events
  - [ ] Events sorted by timestamp descending

  **QA Scenarios**:
  ```
  Scenario: View email tracking
    Tool: Playwright
    Steps:
      1. Open contact profile
      2. Click Emails tab
    Expected Result: Email events timeline visible with color-coded badges
    Evidence: .sisyphus/evidence/task-8-email-tracking.png

  Scenario: Empty email state
    Tool: Playwright
    Steps:
      1. Open contact profile for contact with no emails
      2. Click Emails tab
    Expected Result: "No email events yet" message shown
    Evidence: .sisyphus/evidence/task-8-email-empty.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add email tracking panel component`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 9. **Labels Filter Component** (Dashboard UI)

  **What to do**:
  - Add label filter dropdown to conversation list header (next to search)
  - Fetch labels from WAHA for each session on page load
  - Dropdown shows all labels across sessions with session name
  - Selecting a label filters conversation list to only show conversations with that label
  - Show label badges on conversations (small colored pills)
  - "Clear filter" option to show all conversations
  - API calls:
    - `GET /api/v1/conversations/labels` on page load
    - `GET /api/v1/conversations?label_id=X` when filter selected

  **Must NOT do**: Don't auto-sync DB tags to WAHA labels.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 10 (integration)

  **References**:
  - `dashboard/src/components/ui/select.tsx` — select component
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing pattern

  **Why**: Labels help users organize and filter conversations by category (e.g., "Hot Lead", "Follow Up", "VIP").

  **Acceptance Criteria**:
  - [ ] Label filter dropdown visible in conversation list header
  - [ ] Can filter conversations by label
  - [ ] Label badges shown on conversations
  - [ ] "Clear filter" option available

  **QA Scenarios**:
  ```
  Scenario: Filter by label
    Tool: Playwright
    Steps:
      1. Open conversations page
      2. Click label filter dropdown
      3. Select a label
    Expected Result: Conversations filtered to only show those with selected label
    Evidence: .sisyphus/evidence/task-9-label-filter.png

  Scenario: Clear filter
    Tool: Playwright
    Steps:
      1. Apply a label filter
      2. Click "Clear filter"
    Expected Result: All conversations shown again
    Evidence: .sisyphus/evidence/task-9-label-clear.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add labels filter component`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 10. **Conversation Page Integration** (wire all components together)

  **What to do**:
  - Integrate contact profile panel into conversations page:
    - Click on contact name in conversation header opens profile panel
    - Profile panel slides in from right side
  - Add proposals tab to profile panel
  - Add emails tab to profile panel
  - Add label filter to conversation list header
  - Add label badges to conversation list items
  - Ensure all SWR caches are properly invalidated:
    - After contact update: `mutate(/api/v1/contacts/{id})`
    - After proposal create/update: `mutate(/api/v1/contacts/{id}/proposals)`
    - After label filter change: `mutate(/api/v1/conversations?label_id=X)`
  - Add navigation link to sidebar (if creating separate pages)

  **Must NOT do**: Don't redesign the page layout.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 6-9)
  - **Blocks**: Task 11

  **References**:
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — main conversations page
  - `dashboard/src/components/sidebar.tsx` — sidebar navigation

  **Why**: Integration ensures all components work together seamlessly and provides a cohesive user experience.

  **Acceptance Criteria**:
  - [ ] All components work together without conflicts
  - [ ] Page loads within 3 seconds
  - [ ] SWR caches properly invalidated
  - [ ] Navigation links added (if applicable)

  **QA Scenarios**:
  ```
  Scenario: Full CRM flow
    Tool: Playwright
    Steps:
      1. Open conversations page
      2. Click on a conversation
      3. Click contact name to open profile
      4. Edit contact details and save
      5. Click Proposals tab, create proposal
      6. Click Emails tab, view events
      7. Apply label filter
      8. Clear filter
    Expected Result: All interactions work without errors
    Evidence: .sisyphus/evidence/task-10-integration.png
  ```

  **Commit**: YES
  - Message: `feat(crm): integrate Phase B components into conversations page`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 11. **E2E QA with Playwright**

  **What to do**:
  - Write Playwright tests for all Phase B features:
    - Test contact profile: open, edit, view history
    - Test proposals: create, view, update status, delete
    - Test email tracking: view events, empty state
    - Test labels: filter, assign, clear
  - Test edge cases:
    - Contact with no proposals
    - Contact with no email events
    - Invalid proposal status transition
    - Label filter with no results

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocks**: Final verification

  **Acceptance Criteria**:
  - [ ] All Playwright tests pass
  - [ ] No flaky tests

  **QA Scenarios**:
  ```
  Scenario: Playwright test suite passes
    Tool: Bash
    Steps:
      1. npx playwright test --reporter=list
    Expected Result: All tests pass, 0 failures
    Evidence: .sisyphus/evidence/task-11-playwright-results.txt
  ```

  **Commit**: YES
  - Message: `test(crm): add Phase B E2E Playwright tests`
  - Files: `dashboard/tests/phase-b.spec.ts`

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `deep`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run linter + type checks on all new/modified Python files. Check for: `as any` patterns, empty catches, console.log in prod, hardcoded URLs/keys, unused imports. Verify config.py used for all settings. Verify no port conflicts.
  Output: `Lint [PASS/FAIL] | Type Check [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test cross-feature integration. Save evidence to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

---

## Commit Strategy

- **Wave 0**: `feat(crm): add Phase B DB schema — proposals and email_events tables`
- **Wave 1**: `feat(crm): add Phase B backend APIs — contact profile, proposals, emails, labels`
- **Wave 2**: `feat(crm): add Phase B dashboard UI — contact profile, proposals, emails, labels`
- **Wave 3**: `fix(crm): QA fixes and edge cases`
- Pre-commit: `python3 -m py_compile scripts/*.py` on all changed files

---

## Success Criteria

### Verification Commands
```bash
# Contact profile
curl -s http://127.0.0.1:8001/api/v1/contacts/1  # Expected: 200 OK with full profile

# Proposals
curl -s http://127.0.0.1:8001/api/v1/contacts/1/proposals  # Expected: 200 OK with proposals

# Email tracking
curl -s http://127.0.0.1:8001/api/v1/conversations/1/emails  # Expected: 200 OK with emails

# Labels
curl -s http://127.0.0.1:8001/api/v1/conversations/labels  # Expected: 200 OK with labels
curl -s "http://127.0.0.1:8001/api/v1/conversations?label_id=1"  # Expected: 200 OK filtered
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Contact profile panel works
- [ ] Proposals CRUD works
- [ ] Email tracking displays
- [ ] Labels filter works
- [ ] Existing pipeline still works end-to-end