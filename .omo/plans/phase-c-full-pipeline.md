# Phase C: Full Pipeline — WhatsApp CRM

## TL;DR

> **Quick Summary**: Complete the CRM with email composer, scheduled messages, broadcast lists, and analytics dashboard.
> 
> **Deliverables**:
> - Email composer in conversations (send emails from CRM)
> - Email templates (reusable email templates)
> - Scheduled messages (schedule WhatsApp/email for later)
> - Broadcast lists (bulk messaging to segments)
> - Analytics dashboard (conversion rates, response times, ROI)
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 (DB schema) → Task 2-6 (APIs) → Task 7-11 (UI) → Task 12 (integration) → Task 13 (QA)

---

## Context

### Original Request
User identified the system is evolving into a full CRM. Phase A (Conversation Essentials) and Phase B (CRM Foundations) complete the core CRM. Phase C adds advanced features for scale.

### Phase Progression
- **Phase A** ✅: Conversation Essentials (history, media, presence, templates, tags)
- **Phase B** 🔄: CRM Foundations (contact profile, proposals, email tracking, labels)
- **Phase C** 📋: Full Pipeline (email composer, templates, scheduled messages, broadcast, analytics)

---

## Work Objectives

### Core Objective
Complete the WhatsApp CRM with advanced features for sales and marketing automation.

### Concrete Deliverables
- `POST /api/v1/conversations/{id}/send-email` — send email from conversation
- `GET/POST/PUT/DELETE /api/v1/email-templates` — email template CRUD
- `POST /api/v1/scheduled-messages` — schedule message for later
- `GET/DELETE /api/v1/scheduled-messages` — list/cancel scheduled messages
- `POST /api/v1/broadcasts` — create broadcast list
- `POST /api/v1/broadcasts/{id}/send` — send broadcast
- `GET /api/v1/analytics/dashboard` — analytics data
- Dashboard: Email composer, templates page, scheduled messages, broadcast, analytics

### Definition of Done
- [ ] Can compose and send email from conversation
- [ ] Can create/edit/delete email templates
- [ ] Can schedule WhatsApp/email messages for later
- [ ] Can create broadcast lists and send bulk messages
- [ ] Can view analytics dashboard with key metrics

### Must Have
- Email composer with template support
- Email template CRUD
- Scheduled messages with cancel
- Broadcast lists with segment targeting
- Analytics dashboard with conversion metrics

### Must NOT Have (Guardrails)
- NO Advanced email marketing automation (separate system)
- NO CRM integrations (Salesforce, HubSpot)
- NO Multi-channel campaigns (Phase D)
- NO AI-powered recommendations (Phase D)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: None
- **Framework**: Playwright for UI, curl for API

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (DB Schema):
└── Task 1: DB schema migrations [quick]

Wave 1 (Backend APIs — after schema):
├── Task 2: Email composer API [unspecified-high]
├── Task 3: Email templates API [quick]
├── Task 4: Scheduled messages API [unspecified-high]
├── Task 5: Broadcast lists API [unspecified-high]
└── Task 6: Analytics API [unspecified-high]

Wave 2 (Dashboard UI — after APIs):
├── Task 7: Email composer component [visual-engineering]
├── Task 8: Templates page [visual-engineering]
├── Task 9: Scheduled messages page [visual-engineering]
├── Task 10: Broadcast page [visual-engineering]
└── Task 11: Analytics dashboard [visual-engineering]

Wave 3 (Integration + QA):
├── Task 12: E2E integration [visual-engineering]
└── Task 13: E2E QA with Playwright [deep]

Wave FINAL:
├── Task F1: Plan compliance audit [deep]
├── Task F2: Code quality review [unspecified-high]
└── Task F3: Real manual QA [unspecified-high]
```

---

## TODOs

- [ ] 1. **DB Schema Migrations** (email_templates, scheduled_messages, broadcast tables)

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/migration_crm_phase_c.py`
  - Add `email_templates` table:
    ```sql
    CREATE TABLE IF NOT EXISTS email_templates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      subject TEXT NOT NULL,
      body TEXT NOT NULL,
      variables TEXT DEFAULT '[]',
      category TEXT DEFAULT 'general',
      is_builtin INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_email_templates_category ON email_templates(category);
    ```
  - Add `scheduled_messages` table:
    ```sql
    CREATE TABLE IF NOT EXISTS scheduled_messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      conversation_id INTEGER NOT NULL,
      message_type TEXT NOT NULL CHECK(message_type IN ('whatsapp', 'email')),
      content TEXT NOT NULL,
      subject TEXT,
      scheduled_at TEXT NOT NULL,
      status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed', 'cancelled')),
      sent_at TEXT,
      error TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_scheduled_messages_status ON scheduled_messages(status);
    CREATE INDEX IF NOT EXISTS idx_scheduled_messages_scheduled ON scheduled_messages(scheduled_at);
    ```
  - Add `broadcast_lists` table:
    ```sql
    CREATE TABLE IF NOT EXISTS broadcast_lists (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      segment_type TEXT NOT NULL CHECK(segment_type IN ('tag', 'status', 'custom')),
      segment_value TEXT NOT NULL,
      wa_number_id TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL
    );
    CREATE INDEX IF NOT EXISTS idx_broadcast_lists_wa ON broadcast_lists(wa_number_id);
    ```
  - Add `broadcast_sends` table:
    ```sql
    CREATE TABLE IF NOT EXISTS broadcast_sends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      broadcast_id INTEGER NOT NULL,
      contact_id INTEGER NOT NULL,
      conversation_id INTEGER,
      status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed', 'skipped')),
      sent_at TEXT,
      error TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (broadcast_id) REFERENCES broadcast_lists(id) ON DELETE CASCADE,
      FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
      FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
    );
    CREATE INDEX IF NOT EXISTS idx_broadcast_sends_broadcast ON broadcast_sends(broadcast_id);
    CREATE INDEX IF NOT EXISTS idx_broadcast_sends_status ON broadcast_sends(status);
    ```
  - Seed default email templates:
    - Welcome: "Welcome to [company]!"
    - Follow Up: "Following up on our conversation"
    - Proposal: "Proposal for [project]"
    - Thank You: "Thank you for your business"
    - Meeting Request: "Let's schedule a meeting"
  - Register migration in `main.py`
  - Run migration, verify tables exist

  **Must NOT do**: Don't modify existing tables. Only ADD new tables.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocks**: Tasks 2, 3, 4, 5, 6

  **References**:
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py` — Phase A migration pattern
  - `src/oneai_reach/api/main.py` — migration registration

  **Why**: All Phase C features need new database tables. Creating them upfront ensures all API tasks can proceed in parallel.

  **Acceptance Criteria**:
  - [ ] `email_templates` table created with correct schema
  - [ ] `scheduled_messages` table created with correct schema
  - [ ] `broadcast_lists` table created with correct schema
  - [ ] `broadcast_sends` table created with correct schema
  - [ ] 5 default email templates seeded
  - [ ] Migration registered in `main.py`

  **QA Scenarios**:
  ```
  Scenario: Migration creates tables
    Tool: Bash (sqlite3)
    Steps:
      1. python3 -c "from oneai_reach.infrastructure.database.migration_crm_phase_c import run_phase_c_migration; run_phase_c_migration('data/leads.db')"
      2. sqlite3 data/leads.db ".tables"
    Expected Result: Output includes email_templates, scheduled_messages, broadcast_lists, broadcast_sends
    Evidence: .sisyphus/evidence/task-1-tables.txt

  Scenario: Default templates seeded
    Tool: Bash (sqlite3)
    Steps:
      1. sqlite3 data/leads.db "SELECT COUNT(*) FROM email_templates WHERE is_builtin=1"
    Expected Result: 5
    Evidence: .sisyphus/evidence/task-1-templates.txt
  ```

  **Commit**: YES
  - Message: `feat(crm): add Phase C DB schema — email templates, scheduled messages, broadcasts`
  - Files: `src/oneai_reach/infrastructure/database/migration_crm_phase_c.py`, `src/oneai_reach/api/main.py`

- [ ] 2. **Email Composer API** (send email from conversation)

  **What to do**:
  - Create `POST /api/v1/conversations/{id}/send-email` endpoint
  - Accept body:
    ```json
    {
      "to": "contact@example.com",
      "subject": "Proposal for Website Redesign",
      "body": "Dear John, ...",
      "template_id": 1,
      "variables": {"name": "John", "company": "Acme Corp"}
    }
    ```
  - If `template_id` provided, load template and replace variables
  - Use existing email sending infrastructure (Brevo/SMTP from `senders.py`)
  - Store in `email_events` table with event_type="sent"
  - Return:
    ```json
    {
      "status": "success",
      "data": {
        "event_id": 1,
        "email": "contact@example.com",
        "subject": "Proposal for Website Redesign",
        "sent_at": "2026-04-25T10:00:00"
      }
    }
    ```
  - Add to existing `conversations.py` or create new file

  **Must NOT do**: Don't build email marketing automation. Just single email send.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 7

  **References**:
  - `scripts/senders.py` — existing email sending infrastructure
  - `src/oneai_reach/config/settings.py` — email settings (Brevo/SMTP)
  - `src/oneai_reach/api/v1/conversations.py` — existing conversation endpoints

  **Why**: Email composer allows users to send emails directly from the conversation view, keeping all communication in one place.

  **Acceptance Criteria**:
  - [ ] `POST /api/v1/conversations/1/send-email` sends email
  - [ ] Email event stored in `email_events`
  - [ ] Template variables replaced correctly
  - [ ] 400 returned for missing required fields

  **QA Scenarios**:
  ```
  Scenario: Send email from conversation
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/send-email -H "Content-Type: application/json" -d '{"subject":"Hello","body":"World","to":"test@example.com"}'
    Expected Result: 200 OK with event_id
    Evidence: .sisyphus/evidence/task-2-email-send.json

  Scenario: Send email with template
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/send-email -H "Content-Type: application/json" -d '{"template_id":1,"variables":{"name":"John"},"to":"test@example.com"}'
    Expected Result: 200 OK with event_id, template variables replaced
    Evidence: .sisyphus/evidence/task-2-email-template.json

  Scenario: Missing required fields
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/send-email -H "Content-Type: application/json" -d '{}'
    Expected Result: 400 Bad Request
    Evidence: .sisyphus/evidence/task-2-email-error.txt
  ```

  **Commit**: YES
  - Message: `feat(crm): add email composer API with template support`
  - Files: `src/oneai_reach/api/v1/conversations.py` (or new file)

- [ ] 3. **Email Templates API** (CRUD)

  **What to do**:
  - Create `src/oneai_reach/api/v1/email_templates.py` with router
  - Implement CRUD:
    - `GET /api/v1/email-templates` — list all templates
      - Query params: `?category=general`
      - Returns: `{ status: "success", data: { templates: [...] } }`
    - `POST /api/v1/email-templates` — create template
      - Body: `{ name, subject, body, variables?, category? }`
      - Returns: `{ status: "success", data: { id, name, subject, body } }`
    - `PUT /api/v1/email-templates/{id}` — update template
      - Body: `{ name?, subject?, body?, variables?, category? }`
      - Returns: `{ status: "success", data: { id, name, subject, body } }`
    - `DELETE /api/v1/email-templates/{id}` — delete template
      - Returns: `{ status: "success", data: { deleted: id } }`
  - Register router in `main.py`

  **Must NOT do**: Don't build template versioning. Just simple CRUD.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 8

  **References**:
  - `src/oneai_reach/api/v1/templates.py` — existing quick reply templates CRUD pattern
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_c.py` — email_templates table schema

  **Why**: Email templates allow users to quickly compose emails with pre-written content, saving time and ensuring consistency.

  **Acceptance Criteria**:
  - [ ] CRUD endpoints work
  - [ ] Can filter by category
  - [ ] 404 returned for non-existent template

  **QA Scenarios**:
  ```
  Scenario: Create template
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/email-templates -H "Content-Type: application/json" -d '{"name":"Welcome","subject":"Welcome to {{company}}!","body":"Dear {{name}}, ..."}'
    Expected Result: 200 OK with template id
    Evidence: .sisyphus/evidence/task-3-template-create.json

  Scenario: List templates
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/email-templates
    Expected Result: 200 OK with templates array
    Evidence: .sisyphus/evidence/task-3-template-list.json

  Scenario: Update template
    Tool: Bash (curl)
    Steps:
      1. curl -s -X PUT http://127.0.0.1:8001/api/v1/email-templates/1 -H "Content-Type: application/json" -d '{"subject":"Updated subject"}'
    Expected Result: 200 OK with updated template
    Evidence: .sisyphus/evidence/task-3-template-update.json

  Scenario: Delete template
    Tool: Bash (curl)
    Steps:
      1. curl -s -X DELETE http://127.0.0.1:8001/api/v1/email-templates/1
    Expected Result: 200 OK with deleted id
    Evidence: .sisyphus/evidence/task-3-template-delete.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add email templates CRUD API`
  - Files: `src/oneai_reach/api/v1/email_templates.py`, `src/oneai_reach/api/main.py`

- [ ] 4. **Scheduled Messages API** (schedule for later)

  **What to do**:
  - Create `src/oneai_reach/api/v1/scheduled_messages.py` with router
  - Implement:
    - `POST /api/v1/scheduled-messages` — schedule message
      - Body: `{ conversation_id, message_type, content, subject?, scheduled_at }`
      - Returns: `{ status: "success", data: { id, scheduled_at, status: "pending" } }`
    - `GET /api/v1/scheduled-messages` — list scheduled messages
      - Query params: `?status=pending&conversation_id=1`
      - Returns: `{ status: "success", data: { messages: [...] } }`
    - `DELETE /api/v1/scheduled-messages/{id}` — cancel scheduled message
      - Returns: `{ status: "success", data: { cancelled: id } }`
  - Create background job to send at scheduled time:
    - Use `asyncio` or `threading` to run periodic check
    - Check every 60 seconds for pending messages where `scheduled_at <= now`
    - Send message via WhatsApp (for `message_type=whatsapp`) or email (for `message_type=email`)
    - Update status to `sent` or `failed`
  - Register router in `main.py`

  **Must NOT do**: Don't build recurring messages. Just one-time scheduling.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 9

  **References**:
  - `scripts/senders.py` — existing sending infrastructure
  - `src/oneai_reach/api/v1/conversations.py` — conversation endpoints
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_c.py` — scheduled_messages table schema

  **Why**: Scheduled messages allow users to send messages at optimal times, improving engagement rates.

  **Acceptance Criteria**:
  - [ ] Can schedule message for later
  - [ ] Can list scheduled messages
  - [ ] Can cancel pending messages
  - [ ] Background job sends at scheduled time
  - [ ] Status updated to `sent` or `failed`

  **QA Scenarios**:
  ```
  Scenario: Schedule message
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/scheduled-messages -H "Content-Type: application/json" -d '{"conversation_id":1,"message_type":"whatsapp","content":"Hello!","scheduled_at":"2026-04-26T10:00:00"}'
    Expected Result: 200 OK with id and status "pending"
    Evidence: .sisyphus/evidence/task-4-schedule.json

  Scenario: List scheduled messages
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/scheduled-messages
    Expected Result: 200 OK with messages array
    Evidence: .sisyphus/evidence/task-4-schedule-list.json

  Scenario: Cancel scheduled message
    Tool: Bash (curl)
    Steps:
      1. curl -s -X DELETE http://127.0.0.1:8001/api/v1/scheduled-messages/1
    Expected Result: 200 OK with cancelled id
    Evidence: .sisyphus/evidence/task-4-schedule-cancel.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add scheduled messages API with background job`
  - Files: `src/oneai_reach/api/v1/scheduled_messages.py`, `src/oneai_reach/api/main.py`

- [ ] 5. **Broadcast Lists API** (bulk messaging)

  **What to do**:
  - Create `src/oneai_reach/api/v1/broadcasts.py` with router
  - Implement:
    - `POST /api/v1/broadcasts` — create broadcast
      - Body: `{ name, description?, segment_type, segment_value, wa_number_id }`
      - `segment_type`: "tag" (filter by tag), "status" (filter by conversation status), "custom" (SQL where clause)
      - Returns: `{ status: "success", data: { id, name, segment_type, segment_value } }`
    - `GET /api/v1/broadcasts` — list broadcasts
      - Returns: `{ status: "success", data: { broadcasts: [...] } }`
    - `GET /api/v1/broadcasts/{id}` — get broadcast details with send stats
      - Returns: `{ status: "success", data: { id, name, total_contacts, sent, failed, pending } }`
    - `POST /api/v1/broadcasts/{id}/send` — send broadcast
      - Returns: `{ status: "success", data: { broadcast_id, total_contacts, status: "sending" } }`
    - `DELETE /api/v1/broadcasts/{id}` — delete broadcast
      - Returns: `{ status: "success", data: { deleted: id } }`
  - Segment logic:
    - `tag`: `SELECT * FROM contacts WHERE tags LIKE '%{value}%'`
    - `status`: `SELECT * FROM conversations WHERE status = '{value}'`
    - `custom`: `SELECT * FROM contacts WHERE {value}`
  - Send logic:
    - Get all contacts matching segment
    - Create `broadcast_sends` record for each (status=pending)
    - Send messages sequentially with 1-second delay
    - Update status to `sent` or `failed`
  - Register router in `main.py`

  **Must NOT do**: Don't build A/B testing. Just basic broadcast.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 10

  **References**:
  - `scripts/senders.py` — existing sending infrastructure
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_c.py` — broadcast tables schema
  - `src/oneai_reach/api/v1/conversations.py` — conversation endpoints

  **Why**: Broadcast lists allow users to send bulk messages to targeted segments, enabling marketing campaigns and announcements.

  **Acceptance Criteria**:
  - [ ] Can create broadcast with segment
  - [ ] Can list broadcasts
  - [ ] Can send broadcast to all matching contacts
  - [ ] Send stats tracked (total, sent, failed, pending)

  **QA Scenarios**:
  ```
  Scenario: Create broadcast
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/broadcasts -H "Content-Type: application/json" -d '{"name":"Summer Sale","segment_type":"tag","segment_value":"vip","wa_number_id":"warung_kecantikan"}'
    Expected Result: 200 OK with broadcast id
    Evidence: .sisyphus/evidence/task-5-broadcast-create.json

  Scenario: Send broadcast
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/broadcasts/1/send
    Expected Result: 200 OK with send stats
    Evidence: .sisyphus/evidence/task-5-broadcast-send.json

  Scenario: Get broadcast stats
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/broadcasts/1
    Expected Result: 200 OK with total_contacts, sent, failed, pending
    Evidence: .sisyphus/evidence/task-5-broadcast-stats.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add broadcast lists API with segment targeting`
  - Files: `src/oneai_reach/api/v1/broadcasts.py`, `src/oneai_reach/api/main.py`

- [ ] 6. **Analytics API** (dashboard data)

  **What to do**:
  - Create `GET /api/v1/analytics/dashboard` endpoint
  - Return comprehensive metrics:
    ```json
    {
      "status": "success",
      "data": {
        "overview": {
          "total_contacts": 150,
          "total_conversations": 200,
          "total_messages": 1500,
          "total_proposals": 25,
          "total_emails_sent": 50
        },
        "conversion_rates": {
          "lead_to_contacted": 0.65,
          "contacted_to_replied": 0.35,
          "replied_to_meeting": 0.20,
          "meeting_to_won": 0.50,
          "full_funnel": 0.023
        },
        "response_times": {
          "avg_first_response_minutes": 15,
          "avg_response_minutes": 8
        },
        "email_metrics": {
          "sent": 50,
          "delivered": 48,
          "opened": 35,
          "clicked": 12,
          "bounced": 2,
          "open_rate": 0.73,
          "click_rate": 0.25
        },
        "whatsapp_metrics": {
          "sent": 200,
          "replied": 120,
          "reply_rate": 0.60
        },
        "top_templates": [
          {"id": 1, "name": "Welcome", "uses": 25},
          {"id": 2, "name": "Follow Up", "uses": 18}
        ],
        "daily_trends": [
          {"date": "2026-04-20", "messages": 45, "replies": 12},
          {"date": "2026-04-21", "messages": 52, "replies": 15}
        ]
      }
    }
    ```
  - Query data from: `contacts`, `conversations`, `conversation_messages`, `proposals`, `email_events`, `broadcast_sends`
  - Add to existing `conversations.py` or create new file

  **Must NOT do**: Don't build real-time analytics. Just dashboard snapshot.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Blocks**: Task 11

  **References**:
  - `src/oneai_reach/api/v1/conversations.py` — conversation endpoints
  - `scripts/state_manager.py` — database tables

  **Why**: Analytics dashboard provides visibility into CRM performance, helping users optimize their outreach strategy.

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/analytics/dashboard` returns comprehensive metrics
  - [ ] All metrics calculated correctly
  - [ ] Empty state handled (no data)

  **QA Scenarios**:
  ```
  Scenario: Get analytics
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/analytics/dashboard
    Expected Result: 200 OK with analytics data
    Evidence: .sisyphus/evidence/task-6-analytics.json

  Scenario: Analytics with no data
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/analytics/dashboard
    Expected Result: 200 OK with zero values
    Evidence: .sisyphus/evidence/task-6-analytics-empty.json
  ```

  **Commit**: YES
  - Message: `feat(crm): add analytics API with comprehensive metrics`
  - Files: `src/oneai_reach/api/v1/analytics.py`, `src/oneai_reach/api/main.py`

- [ ] 7. **Email Composer Component** (Dashboard UI)

  **What to do**:
  - Add email composer to conversation view (next to WhatsApp reply input)
  - Toggle between WhatsApp and Email mode
  - Email mode shows:
    - To field (pre-filled with contact email)
    - Subject input
    - Template selector dropdown
    - Body textarea
    - Send button
  - Template selector:
    - Fetch templates from `GET /api/v1/email-templates`
    - Selecting template fills subject and body
    - Variables shown as `{{name}}` placeholders
  - Variable auto-fill:
    - When template selected, replace `{{name}}` with contact name
    - Replace `{{company}}` with contact company
  - Send confirmation dialog before sending
  - API calls:
    - `GET /api/v1/email-templates` on component mount
    - `POST /api/v1/conversations/{id}/send-email` on send

  **Must NOT do**: Don't build email marketing automation. Just single email send.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing conversation page
  - `dashboard/src/components/ui/textarea.tsx` — textarea component
  - `dashboard/src/components/ui/select.tsx` — select component

  **Why**: Email composer allows users to send emails directly from the conversation view, keeping all communication in one place.

  **Acceptance Criteria**:
  - [ ] Email composer visible in conversation
  - [ ] Can toggle between WhatsApp and Email mode
  - [ ] Can select template and send
  - [ ] Variables auto-filled from contact data

  **QA Scenarios**:
  ```
  Scenario: Send email
    Tool: Playwright
    Steps:
      1. Open conversation
      2. Click "Email" toggle
      3. Fill in subject and body
      4. Click Send
    Expected Result: Email sent, success message shown
    Evidence: .sisyphus/evidence/task-7-email-send.png

  Scenario: Use template
    Tool: Playwright
    Steps:
      1. Open email composer
      2. Select template from dropdown
    Expected Result: Subject and body filled with template content, variables replaced
    Evidence: .sisyphus/evidence/task-7-email-template.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add email composer component`
  - Files: `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 8. **Templates Page** (Dashboard UI)

  **What to do**:
  - Create `/email-templates` page in dashboard
  - List email templates in table:
    - Columns: Name, Subject, Category, Created, Actions
    - Actions: Edit, Delete
  - "New Template" button opens dialog:
    - Name input
    - Subject input
    - Body textarea
    - Category select (general, follow-up, proposal, welcome)
    - Variables help text
  - Edit template: opens dialog with pre-filled values
  - Delete template: confirmation dialog
  - Preview template: shows rendered preview with sample variables
  - API calls:
    - `GET /api/v1/email-templates` on page load
    - `POST /api/v1/email-templates` on create
    - `PUT /api/v1/email-templates/{id}` on edit
    - `DELETE /api/v1/email-templates/{id}` on delete

  **Must NOT do**: Don't build template versioning. Just simple CRUD UI.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing page pattern
  - `dashboard/src/components/ui/dialog.tsx` — dialog component
  - `dashboard/src/components/ui/table.tsx` — table component

  **Why**: Templates page allows users to manage email templates centrally, ensuring consistency across the team.

  **Acceptance Criteria**:
  - [ ] Templates page shows list of templates
  - [ ] Can create new template
  - [ ] Can edit existing template
  - [ ] Can delete template with confirmation

  **QA Scenarios**:
  ```
  Scenario: Create template
    Tool: Playwright
    Steps:
      1. Navigate to /email-templates
      2. Click "New Template"
      3. Fill in name, subject, body
      4. Click Save
    Expected Result: Template appears in list
    Evidence: .sisyphus/evidence/task-8-template-create.png

  Scenario: Edit template
    Tool: Playwright
    Steps:
      1. Click Edit on a template
      2. Change subject
      3. Click Save
    Expected Result: Template updated in list
    Evidence: .sisyphus/evidence/task-8-template-edit.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add email templates page`
  - Files: `dashboard/src/app/(dashboard)/email-templates/page.tsx`

- [ ] 9. **Scheduled Messages Page** (Dashboard UI)

  **What to do**:
  - Create `/scheduled` page in dashboard
  - List scheduled messages in table:
    - Columns: Type, Content, Scheduled At, Status, Actions
    - Status badges: pending (yellow), sent (green), failed (red), cancelled (gray)
    - Actions: Cancel (only for pending)
  - "New Scheduled Message" button opens dialog:
    - Conversation selector
    - Message type toggle (WhatsApp/Email)
    - Content textarea
    - Subject input (for email)
    - Date/time picker for scheduled_at
  - Cancel button: confirmation dialog
  - Auto-refresh every 30 seconds to show status updates
  - API calls:
    - `GET /api/v1/scheduled-messages` on page load
    - `POST /api/v1/scheduled-messages` on create
    - `DELETE /api/v1/scheduled-messages/{id}` on cancel

  **Must NOT do**: Don't build recurring messages. Just one-time scheduling UI.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing page pattern
  - `dashboard/src/components/ui/dialog.tsx` — dialog component
  - `dashboard/src/components/ui/table.tsx` — table component

  **Why**: Scheduled messages page allows users to plan their outreach and send messages at optimal times.

  **Acceptance Criteria**:
  - [ ] Scheduled messages page shows list
  - [ ] Can create new scheduled message
  - [ ] Can cancel pending messages
  - [ ] Status badges shown correctly

  **QA Scenarios**:
  ```
  Scenario: Schedule message
    Tool: Playwright
    Steps:
      1. Navigate to /scheduled
      2. Click "New Scheduled Message"
      3. Fill in content and scheduled_at
      4. Click Save
    Expected Result: Message appears in list with "pending" status
    Evidence: .sisyphus/evidence/task-9-schedule-create.png

  Scenario: Cancel message
    Tool: Playwright
    Steps:
      1. Click Cancel on a pending message
      2. Confirm cancellation
    Expected Result: Message status changes to "cancelled"
    Evidence: .sisyphus/evidence/task-9-schedule-cancel.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add scheduled messages page`
  - Files: `dashboard/src/app/(dashboard)/scheduled/page.tsx`

- [ ] 10. **Broadcast Page** (Dashboard UI)

  **What to do**:
  - Create `/broadcasts` page in dashboard
  - List broadcasts in table:
    - Columns: Name, Segment, Total Contacts, Sent, Failed, Status, Actions
    - Status badges: draft (gray), sending (yellow), completed (green)
    - Actions: Send, Delete
  - "New Broadcast" button opens dialog:
    - Name input
    - Description textarea
    - Segment type select (tag, status, custom)
    - Segment value input
    - WA number selector
  - Send button:
    - Shows confirmation with contact count
    - Shows progress during send
  - Broadcast detail view:
    - Shows send stats (total, sent, failed, pending)
    - List of contacts with send status
  - API calls:
    - `GET /api/v1/broadcasts` on page load
    - `POST /api/v1/broadcasts` on create
    - `POST /api/v1/broadcasts/{id}/send` on send
    - `GET /api/v1/broadcasts/{id}` for detail view

  **Must NOT do**: Don't build A/B testing. Just basic broadcast UI.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — existing page pattern
  - `dashboard/src/components/ui/dialog.tsx` — dialog component
  - `dashboard/src/components/ui/table.tsx` — table component

  **Why**: Broadcast page allows users to send bulk messages to targeted segments, enabling marketing campaigns.

  **Acceptance Criteria**:
  - [ ] Broadcast page shows list
  - [ ] Can create new broadcast with segment
  - [ ] Can send broadcast
  - [ ] Send stats shown

  **QA Scenarios**:
  ```
  Scenario: Create broadcast
    Tool: Playwright
    Steps:
      1. Navigate to /broadcasts
      2. Click "New Broadcast"
      3. Fill in name and segment
      4. Click Save
    Expected Result: Broadcast appears in list
    Evidence: .sisyphus/evidence/task-10-broadcast-create.png

  Scenario: Send broadcast
    Tool: Playwright
    Steps:
      1. Click Send on a broadcast
      2. Confirm send
    Expected Result: Broadcast sent, stats updated
    Evidence: .sisyphus/evidence/task-10-broadcast-send.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add broadcast page`
  - Files: `dashboard/src/app/(dashboard)/broadcasts/page.tsx`

- [ ] 11. **Analytics Dashboard** (Dashboard UI)

  **What to do**:
  - Create `/analytics` page in dashboard (or enhance existing)
  - Show key metrics cards:
    - Total Contacts
    - Total Conversations
    - Total Messages
    - Reply Rate
    - Email Open Rate
  - Charts:
    - Line chart: Daily messages trend (last 30 days)
    - Bar chart: Conversion funnel (lead → contacted → replied → meeting → won)
    - Pie chart: Email metrics (sent, delivered, opened, clicked, bounced)
    - Table: Top performing templates
  - Use `recharts` library (already installed)
  - API calls:
    - `GET /api/v1/analytics/dashboard` on page load

  **Must NOT do**: Don't build real-time analytics. Just dashboard snapshot.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12

  **References**:
  - `dashboard/src/app/(dashboard)/analytics/page.tsx` — existing analytics page
  - `recharts` — chart library

  **Why**: Analytics dashboard provides visibility into CRM performance, helping users optimize their outreach strategy.

  **Acceptance Criteria**:
  - [ ] Analytics dashboard shows metrics
  - [ ] Charts display trends
  - [ ] Empty state handled

  **QA Scenarios**:
  ```
  Scenario: View analytics
    Tool: Playwright
    Steps:
      1. Navigate to /analytics
    Expected Result: Dashboard shows metrics and charts
    Evidence: .sisyphus/evidence/task-11-analytics.png

  Scenario: Analytics with no data
    Tool: Playwright
    Steps:
      1. Navigate to /analytics with no data
    Expected Result: Dashboard shows zero values and empty charts
    Evidence: .sisyphus/evidence/task-11-analytics-empty.png
  ```

  **Commit**: YES
  - Message: `feat(crm): add analytics dashboard`
  - Files: `dashboard/src/app/(dashboard)/analytics/page.tsx`

- [ ] 12. **E2E Integration**

  **What to do**:
  - Wire all Phase C components together
  - Add navigation links to sidebar:
    - Email Templates
    - Scheduled Messages
    - Broadcasts
    - Analytics (if not exists)
  - Ensure all SWR caches are properly invalidated
  - Test full flow:
    - Create email template
    - Send email using template
    - Schedule message
    - Create and send broadcast
    - View analytics

  **Must NOT do**: Don't redesign the page layout.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 7-11)
  - **Blocks**: Task 13

  **References**:
  - `dashboard/src/components/sidebar.tsx` — sidebar navigation
  - `dashboard/src/app/(dashboard)/conversations/page.tsx` — main conversations page

  **Why**: Integration ensures all components work together seamlessly and provides a cohesive user experience.

  **Acceptance Criteria**:
  - [ ] All components work together without conflicts
  - [ ] Navigation links added to sidebar
  - [ ] SWR caches properly invalidated

  **QA Scenarios**:
  ```
  Scenario: Full Phase C flow
    Tool: Playwright
    Steps:
      1. Create email template
      2. Send email using template
      3. Schedule message
      4. Create broadcast
      5. Send broadcast
      6. View analytics
    Expected Result: All interactions work
    Evidence: .sisyphus/evidence/task-12-integration.png
  ```

  **Commit**: YES
  - Message: `feat(crm): integrate Phase C components`
  - Files: `dashboard/src/components/sidebar.tsx`, `dashboard/src/app/(dashboard)/conversations/page.tsx`

- [ ] 13. **E2E QA with Playwright**

  **What to do**:
  - Write Playwright tests for all Phase C features:
    - Test email composer: send email, use template
    - Test templates: create, edit, delete
    - Test scheduled messages: create, cancel
    - Test broadcasts: create, send
    - Test analytics: view dashboard
  - Test edge cases:
    - Template with no variables
    - Scheduled message in the past
    - Broadcast with no contacts
    - Analytics with no data

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
    Evidence: .sisyphus/evidence/task-13-playwright-results.txt
  ```

  **Commit**: YES
  - Message: `test(crm): add Phase C E2E Playwright tests`
  - Files: `dashboard/tests/phase-c.spec.ts`

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

- **Wave 0**: `feat(crm): add Phase C DB schema — email templates, scheduled messages, broadcasts`
- **Wave 1**: `feat(crm): add Phase C backend APIs — email, templates, scheduled, broadcast, analytics`
- **Wave 2**: `feat(crm): add Phase C dashboard UI — email composer, templates, scheduled, broadcast, analytics`
- **Wave 3**: `fix(crm): QA fixes and edge cases`
- Pre-commit: `python3 -m py_compile scripts/*.py` on all changed files

---

## Success Criteria

### Verification Commands
```bash
# Email composer
curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/send-email -H "Content-Type: application/json" -d '{"subject":"Hello","body":"...","to":"test@example.com"}'

# Templates
curl -s http://127.0.0.1:8001/api/v1/email-templates

# Scheduled messages
curl -s http://127.0.0.1:8001/api/v1/scheduled-messages

# Broadcasts
curl -s http://127.0.0.1:8001/api/v1/broadcasts

# Analytics
curl -s http://127.0.0.1:8001/api/v1/analytics/dashboard
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Email composer works
- [ ] Templates CRUD works
- [ ] Scheduled messages work
- [ ] Broadcast lists work
- [ ] Analytics dashboard works
- [ ] Existing pipeline still works end-to-end