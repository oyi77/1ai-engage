# Phase A: Conversation Essentials — WhatsApp CRM

## TL;DR

> **Quick Summary**: Make the conversation room a usable daily tool by adding message history, media sending, presence tracking, quick reply templates, and @lid contact merging.
> 
> **Deliverables**:
> - Infinite scroll message history loaded from WAHA on-demand with pre-load
> - Image/file/video/voice attachment sending in conversation room
> - Online/offline/composing presence indicators per contact
> - Quick reply template picker (CRUD templates, one-click send)
> - @lid auto-merge: link encrypted contacts to known @c.us by push_name
> - Dual tagging system: WAHA native labels + DB tags on conversations
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: Task 1 (DB schema) → Task 5 (WAHA proxy) → Tasks 6-9 (features) → Task 10-11 (UI integration) → Task 12 (QA)

---

## Context

### Original Request
User identified 7 missing features in the conversation room and recognized the system is evolving into a full CRM. Wants Phase A (Conversation Essentials) built first.

### Interview Summary
**Key Discussions**:
- @lid contacts: WhatsApp encrypted ID, can't be reversed to phone number, but CAN merge by push_name match
- Message history: On-demand from WAHA with pre-load of last 50 messages (WAHA is source of truth)
- Tags: Dual system — WAHA native labels (syncs to phone app) + our own DB tags (flexible, unlimited)
- Phase priority: Conversation Essentials first, then CRM Foundations, then Full Pipeline

**Research Findings**:
- WAHA has full Presence API: `GET /api/:session/presence`, `POST /api/:session/presence`
- WAHA has Labels API: `GET/POST/PUT/DELETE /api/:session/labels` with name + color
- WAHA has sendImage, sendFile, sendVideo, sendVoice endpoints
- WAHA messages endpoint: `GET /api/chats/:chatId/messages` with pagination (limit, offset)
- `@lid` is WhatsApp's privacy feature from 2024 — encrypted, one-way, no reverse resolution
- Dashboard is Next.js + SWR, conversations page at 508 lines, auto-refresh 5s/3s

### Metis Review (Self-conducted)
**Identified Gaps** (addressed):
- Media size limits not specified → cap at 10MB per file, WAHA may have its own limits
- @lid merge false positives → require exact push_name match + same session context
- Message dedup when loading history → WAHA message IDs already deduplicated in webhook handler
- Presence stale data → poll every 15s, show "last seen" timestamp
- Template permissions → all templates shared across all WA numbers for now

---

## Work Objectives

### Core Objective
Transform the conversation room from a basic text-only chat viewer into a fully functional daily CRM tool with history, media, presence, templates, and proper contact handling.

### Concrete Deliverables
- `GET /api/v1/conversations/{id}/waha-history` endpoint for loading older messages from WAHA
- `POST /api/v1/conversations/{id}/send-media` endpoint for sending images/files/videos/voice
- `GET /api/v1/presence/{session}` endpoint for online/offline status
- `POST /api/v1/presence/{session}/subscribe` endpoint to subscribe to presence updates
- `GET/POST/PUT/DELETE /api/v1/templates` endpoints for quick reply templates
- `GET/POST/PUT/DELETE /api/v1/conversations/{id}/tags` endpoints for DB tags
- `GET/POST/DELETE /api/v1/labels/{session}` proxy endpoints for WAHA labels
- Auto-merge @lid contacts in webhook handler
- Dashboard UI: infinite scroll, attachment picker, presence dots, template picker, tag badges

### Definition of Done
- [ ] Can scroll up in conversation to load 50+ older messages from WAHA history
- [ ] Can attach and send an image file to a WhatsApp contact
- [ ] Can see if a contact is online/offline in the conversation list
- [ ] Can select a quick reply template and send it with one click
- [ ] @lid contacts auto-merge into existing @c.us conversations when push_name matches
- [ ] Can add/remove tags on conversations and see them in the UI
- [ ] WAHA labels sync with the dashboard (create, view, assign)

### Must Have
- Infinite scroll message loading (not just "load more" button)
- Media upload with drag-and-drop and file picker
- Presence indicator (online dot / last seen timestamp)
- Template CRUD (create, read, update, delete)
- @lid → @c.us auto-merge by push_name
- Tag system for conversations

### Must NOT Have (Guardrails)
- NO Contact profile panel (Phase B)
- NO Proposals page (Phase B)
- NO Email tracking in conversations (Phase B)
- NO Scheduled messages (Phase C)
- NO Broadcast lists (Phase C)
- NO Analytics dashboard (Phase C)
- NO AI slop: over-engineered abstractions, excessive JSDoc, generic variable names
- NO Mobile-responsive redesign (out of scope, existing layout is fine)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (no new test framework needed, verify via API + Playwright)
- **Automated tests**: None (tests-after in Phase B if needed)
- **Framework**: Playwright for UI, curl for API

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Playwright — navigate, interact, assert DOM, screenshot
- **API/Backend**: curl — send requests, assert status + response fields

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — DB schema + WAHA proxy):
├── Task 1: DB schema migrations (tags, templates, @lid mapping) [quick]
├── Task 2: WAHA API proxy endpoints (messages, media, presence, labels) [deep]
└── Task 3: @lid auto-merge logic in webhook handler [quick]

Wave 2 (Core backend — after schema + proxy):
├── Task 4: Message history API endpoint [unspecified-high]
├── Task 5: Media upload + send endpoint [unspecified-high]
├── Task 6: Presence tracking endpoint + webhook [unspecified-high]
├── Task 7: Quick reply templates CRUD endpoints [quick]
└── Task 8: Tags CRUD endpoints + WAHA labels sync [quick]

Wave 3 (Dashboard UI — after all backend):
├── Task 9: Infinite scroll message history component [visual-engineering]
├── Task 10: Media upload attachment picker component [visual-engineering]
├── Task 11: Presence indicator component (online dot / last seen) [visual-engineering]
├── Task 12: Quick reply template picker + tag badges [visual-engineering]
└── Task 13: Conversation page integration (wire all components) [visual-engineering]

Wave 4 (QA + verification):
├── Task 14: End-to-end QA with Playwright [deep]
└── Task 15: Performance + edge case testing [deep]

Wave FINAL (Independent review):
├── Task F1: Plan compliance audit [deep]
├── Task F2: Code quality review [unspecified-high]
└── Task F3: Real manual QA [unspecified-high]

Critical Path: Task 1 → Task 4 → Task 9 → Task 14
Parallel Speedup: ~60% faster than sequential
```

### Agent Dispatch Summary
- **Wave 1**: T1→`quick`, T2→`deep`, T3→`quick`
- **Wave 2**: T4→`unspecified-high`, T5→`unspecified-high`, T6→`unspecified-high`, T7→`quick`, T8→`quick`
- **Wave 3**: T9-T13→`visual-engineering`
- **Wave 4**: T14-T15→`deep`
- **FINAL**: F1→`deep`, F2→`unspecified-high`, F3→`unspecified-high`

---

## TODOs

- [x] 1. **DB Schema Migrations** (tags, templates, @lid mapping)

  **What to do**:
  - Create migration file `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py`
  - Add `conversation_tags` table: `id, conversation_id, tag, created_at` (FK to conversations)
  - Add `quick_reply_templates` table: `id, wa_number_id, name, content, category, created_at, updated_at`
  - Add `contact_jid_map` table: `id, wa_number_id, lid, c_us_phone, push_name, confidence, created_at` (maps @lid→@c.us)
  - Add `presence_status` table: `id, wa_number_id, contact_phone, status (online/offline/composing), last_seen_at, updated_at`
  - Add `media_messages` table: `id, conversation_id, message_id, media_type, file_url, file_name, file_size, caption, created_at`
  - Register migration in `migration_v2.py` (or new migration runner)
  - Run migration, verify tables exist

  **Must NOT do**: Don't modify existing tables (conversations, messages). Only ADD new tables.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5, 6, 7, 8 (all need schema)
  - **Blocked By**: None

  **References**:
  - `src/oneai_reach/infrastructure/database/migration_v2.py` — existing migration pattern
  - `src/oneai_reach/infrastructure/database/migration_personas.py` — another migration example
  - `scripts/state_manager.py` lines 88-142 — existing DB schema (conversations, conversation_messages, wa_numbers)

  **Why**: The migration pattern uses SQLite with manual schema creation. Follow the same pattern — don't introduce Alembic or SQLAlchemy migrations.

  **Acceptance Criteria**:
  - [ ] New tables created: conversation_tags, quick_reply_templates, contact_jid_map, presence_status, media_messages
  - [ ] Migration runs without errors
  - [ ] Existing data untouched (conversations, leads, etc. still intact)

  **QA Scenarios**:
  ```
  Scenario: Migration creates all tables
    Tool: Bash (sqlite3)
    Preconditions: Clean DB or existing DB
    Steps:
      1. Run: python3 -c "from oneai_reach.infrastructure.database.migration_crm_phase_a import migrate; migrate()"
      2. Run: sqlite3 data/1ai_reach.db ".tables"
    Expected Result: Output includes conversation_tags, quick_reply_templates, contact_jid_map, presence_status, media_messages
    Evidence: .sisyphus/evidence/task-1-tables-created.txt
  ```

  **Commit**: YES (group with Wave 1)
  - Message: `feat(crm): add Phase A DB schema migrations`
  - Files: `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py`, migration registration

- [x] 2. **WAHA API Proxy Endpoints** (messages, media, presence, labels)

  **What to do**:
  - Create `src/oneai_reach/api/v1/waha_proxy.py` with router
  - Implement proxy endpoints that forward to WAHA with our API key:
    - `GET /api/v1/waha/{session}/chats/{chat_id}/messages` — proxy to WAHA `GET /api/chats/{chatId}/messages` with pagination params
    - `POST /api/v1/waha/{session}/sendImage` — proxy to WAHA `POST /api/:session/sendImage`
    - `POST /api/v1/waha/{session}/sendFile` — proxy to WAHA `POST /api/:session/sendFile`
    - `POST /api/v1/waha/{session}/sendVideo` — proxy to WAHA `POST /api/:session/sendVideo`
    - `POST /api/v1/waha/{session}/sendVoice` — proxy to WAHA `POST /api/:session/sendVoice`
    - `GET /api/v1/waha/{session}/presence` — proxy to WAHA `GET /api/:session/presence`
    - `POST /api/v1/waha/{session}/presence` — proxy to WAHA `POST /api/:session/presence` (subscribe)
    - `GET /api/v1/waha/{session}/labels` — proxy to WAHA labels CRUD
    - `POST/PUT/DELETE /api/v1/waha/{session}/labels` — proxy to WAHA labels CRUD
  - Add authentication (reuse existing `verify_api_key`)
  - Add error handling (WAHA downtime, session not found)
  - Register router in `src/oneai_reach/api/main.py`

  **Must NOT do**: Don't build business logic here — this is a pure proxy layer. Business logic goes in the feature-specific endpoints (Tasks 4-8).

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 4, 5, 6, 8 (need proxy endpoints)
  - **Blocked By**: None

  **References**:
  - `src/oneai_reach/api/v1/agents.py` — existing router with WAHA session handling (see `wa_sessions` endpoint)
  - `src/oneai_reach/config/settings.py` — `PROXY_URL` and `PROXY_KEY` constants for WAHA connection
  - WAHA source: `/home/openclaw/projects/waha/src/api/chatting.controller.ts` — sendImage, sendFile, sendVideo, sendVoice endpoints
  - WAHA source: `/home/openclaw/projects/waha/src/api/presence.controller.ts` — presence endpoints
  - WAHA source: `/home/openclaw/projects/waha/src/api/labels.controller.ts` — labels CRUD
  - WAHA source: `/home/openclaw/projects/waha/src/api/chats.controller.ts` — messages endpoint with pagination

  **Why**: WAHA Plus is at `https://waha.aitradepulse.com` with key `199c96bcb87e45a39f6cde9e5677ed09`. The proxy forwards requests to this host. Follow the existing pattern in agents.py for WAHA session handling.

  **Acceptance Criteria**:
  - [ ] All proxy endpoints return WAHA responses with correct status codes
  - [ ] Authentication required (API key check)
  - [ ] 404 returned for non-existent sessions

  **QA Scenarios**:
  ```
  Scenario: WAHA presence proxy works
    Tool: Bash (curl)
    Preconditions: WAHA running, session warung_kecantikan active
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/waha/warung_kecantikan/presence -H "X-API-Key: test"
    Expected Result: 200 OK with presence JSON array
    Evidence: .sisyphus/evidence/task-2-presence-proxy.json

  Scenario: WAHA labels proxy works
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/waha/warung_kecantikan/labels -H "X-API-Key: test"
    Expected Result: 200 OK with labels JSON array (may be empty)
    Evidence: .sisyphus/evidence/task-2-labels-proxy.json

  Scenario: Message history proxy works
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://127.0.0.1:8001/api/v1/waha/warung_kecantikan/chats/6281234567890@c.us/messages?limit=10" -H "X-API-Key: test"
    Expected Result: 200 OK with messages array
    Evidence: .sisyphus/evidence/task-2-messages-proxy.json
  ```

  **Commit**: YES (group with Wave 1)

- [x] 3. **@lid Auto-Merge Logic** in webhook handler

  **What to do**:
  - In `src/oneai_reach/api/webhooks/waha.py`, after JID normalization:
    - If sender contains `@lid`, query `contact_jid_map` table for a mapping to a `@c.us` phone number
    - If mapping found: replace sender with the `@c.us` phone number so the rest of the pipeline works normally
    - If no mapping: check if the WAHA payload has `pushName` field. If yes, look for an existing `@c.us` conversation in this session with the same `push_name`. If found, create a mapping entry in `contact_jid_map` with `confidence=auto`, then use the `@c.us` phone
    - If no match: store the @lid as-is, but add `push_name` to `contact_name` for display. The conversation will be separate until manually merged.
  - Add API endpoint `POST /api/v1/conversations/{id}/merge` for manual merge (merge two conversations into one)
  - Add the `pushName` field extraction to `_extract_body` or a new helper function

  **Must NOT do**: Don't merge @lid contacts aggressively — false positives create worse problems than duplicates. Only merge on exact push_name match.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: None (standalone logic)
  - **Blocked By**: Task 1 (needs contact_jid_map table)

  **References**:
  - `src/oneai_reach/api/webhooks/waha.py` — webhook handler, `_normalize_jid()` function, sender extraction
  - WAHA webhook payload includes `pushName` field in message events
  - `scripts/state_manager.py` — `normalize_jid()` function (already handles @lid preservation)
  - `scripts/state_manager.py` — `get_or_create_conversation()` (where @lid phone gets stored)

  **Why**: The `_normalize_jid()` function currently preserves @lid as-is. We need to add a lookup step BEFORE that normalization, checking if we've seen this @lid before and mapped it to a known @c.us contact.

  **Acceptance Criteria**:
  - [ ] @lid message with matching pushName gets redirected to existing @c.us conversation
  - [ ] @lid message without match creates separate conversation with pushName as contact_name
  - [ ] Manual merge endpoint works: `POST /api/v1/conversations/{id}/merge` combines two conversations

  **QA Scenarios**:
  ```
  Scenario: Known @lid auto-merged to @c.us
    Tool: Bash (curl)
    Preconditions: Contact_jid_map has entry mapping lid123@lid → 628123456789@c.us for warung_kecantikan
    Steps:
      1. Send webhook with from=lid123@lid and pushName="John"
      2. Check conversation created/found uses 628123456789@c.us
    Expected Result: Message appears in existing @c.us conversation, not a new @lid conversation
    Evidence: .sisyphus/evidence/task-3-lid-merge.txt

  Scenario: Unknown @lid creates separate conversation
    Tool: Bash (curl)
    Steps:
      1. Send webhook with from=newlid456@lid and pushName="Unknown Person"
      2. Check conversation uses lid456@lid as contact_phone, "Unknown Person" as contact_name
    Expected Result: New conversation created with @lid phone and pushName as display name
    Evidence: .sisyphus/evidence/task-3-lid-separate.txt
  ```

  **Commit**: YES (group with Wave 1)

- [x] 4. **Message History API Endpoint**

  **What to do**:
  - Create `GET /api/v1/conversations/{id}/waha-history` endpoint
  - Accept `?limit=50&before=<timestamp>` pagination params
  - Call WAHA proxy `GET /api/v1/waha/{session}/chats/{contact_phone}/messages?limit=50`
  - Transform WAHA response format to our message format (direction, text, timestamp, sender)
  - Deduplicate against our existing `conversation_messages` (by `waha_message_id`)
  - Store loaded messages in our DB so they don't need re-fetching
  - Return merged results (our messages + WAHA history) sorted by timestamp

  **Must NOT do**: Don't store ALL WhatsApp history permanently on first load. Only cache what's viewed. WAHA remains source of truth for history.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 9 (infinite scroll UI needs this endpoint)
  - **Blocked By**: Task 1 (schema), Task 2 (proxy)

  **References**:
  - `src/oneai_reach/api/v1/conversations.py` — existing conversation endpoints, message format
  - `scripts/state_manager.py` — `get_conversation_messages()` (current 50-limit fetch)
  - WAHA source: `/home/openclaw/projects/waha/src/api/chats.controller.ts` — messages endpoint accepts `limit`, `offset`, `sort` params
  - `src/oneai_reach/api/webhooks/waha.py` — `_extract_body()` for NOWEB format messages

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/conversations/1/waha-history?limit=50` returns messages from WAHA
  - [ ] Messages are deduplicated (no duplicate waha_message_ids)
  - [ ] Pagination works: `?before=<timestamp>` returns older messages

  **QA Scenarios**:
  ```
  Scenario: Load history for existing conversation
    Tool: Bash (curl)
    Steps:
      1. curl -s "http://127.0.0.1:8001/api/v1/conversations/1/waha-history?limit=50"
    Expected Result: 200 OK, JSON with messages array containing WAHA history messages
    Failure Indicators: 500 error, empty array, duplicate messages
    Evidence: .sisyphus/evidence/task-4-history-load.json

  Scenario: Pagination loads older messages
    Tool: Bash (curl)
    Steps:
      1. First call: curl history?limit=5
      2. Get oldest timestamp from response
      3. Second call: curl history?limit=5&before=<oldest_timestamp>
    Expected Result: Second call returns 5 messages OLDER than the timestamp (no overlap with first call)
    Evidence: .sisyphus/evidence/task-4-history-pagination.json
  ```

  **Commit**: YES (group with Wave 2)

- [x] 5. **Media Upload + Send Endpoint**

  **What to do**:
  - Create `POST /api/v1/conversations/{id}/send-media` endpoint
  - Accept multipart form: `file` (binary), `type` (image/video/document/voice), `caption` (optional text)
  - Validate file: max 10MB, allowed types (jpg, png, gif, pdf, mp4, ogg, mp3)
  - Upload file to WAHA via proxy `POST /api/v1/waha/{session}/sendImage` (or sendFile/sendVideo/sendVoice based on type)
  - Store media info in `media_messages` table linked to the conversation
  - Also store a text message in `conversation_messages` with `message_type` set to the media type
  - Return success with message ID and media URL

  **Must NOT do**: Don't store media files locally. WAHA handles the actual upload to WhatsApp servers. We just proxy.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 10 (attachment picker UI)
  - **Blocked By**: Task 1 (schema), Task 2 (proxy)

  **References**:
  - `src/oneai_reach/api/v1/conversations.py` — existing `api_conversation_send()` for text messages
  - `scripts/senders.py` — `send_whatsapp_session()` and `_send_wa_waha_raw()` for WAHA sending
  - WAHA source: `/home/openclaw/projects/waha/src/api/chatting.controller.ts` — sendImage request body format

  **Acceptance Criteria**:
  - [ ] Can upload image file and send to WhatsApp conversation
  - [ ] File size > 10MB rejected with 413
  - [ ] Invalid file type rejected with 400
  - [ ] Media message appears in conversation_messages with correct type

  **QA Scenarios**:
  ```
  Scenario: Send image to conversation
    Tool: Bash (curl)
    Steps:
      1. Create a test image: convert -size 100x100 xc:red /tmp/test_image.jpg
      2. curl -s -X POST -F "file=@/tmp/test_image.jpg" -F "type=image" -F "caption=Test caption" http://127.0.0.1:8001/api/v1/conversations/1/send-media
    Expected Result: 200 OK, response contains message_id and "sent" status
    Evidence: .sisyphus/evidence/task-5-media-send.json

  Scenario: Reject oversized file
    Tool: Bash (curl)
    Steps:
      1. Create a 15MB file: dd if=/dev/zero of=/tmp/large.bin bs=1M count=15
      2. curl -s -X POST -F "file=@/tmp/large.bin" -F "type=document" http://127.0.0.1:8001/api/v1/conversations/1/send-media
    Expected Result: 413 Payload Too Large
    Evidence: .sisyphus/evidence/task-5-media-size-limit.txt
  ```

  **Commit**: YES (group with Wave 2)

- [x] 6. **Presence Tracking Endpoint + Webhook**

  **What to do**:
  - Create `GET /api/v1/presence/{session}` — returns current presence status for all chats in session
  - Create `POST /api/v1/presence/{session}/subscribe` — subscribes to presence updates via WAHA
  - Add presence webhook handler in `src/oneai_reach/api/webhooks/waha.py` for `session.presence` events
  - Store presence status in `presence_status` table (update on upsert)
  - Include presence data in conversations API response: `online`, `offline`, `composing`, `last_seen_at`
  - Auto-subscribe to presence when a conversation is first opened in dashboard (via frontend call)

  **Must NOT do**: Don't poll WAHA presence every 5 seconds. Subscribe once per session, receive webhook updates.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 11 (presence indicator UI)
  - **Blocked By**: Task 1 (schema), Task 2 (proxy)

  **References**:
  - `src/oneai_reach/api/webhooks/waha.py` — existing webhook handler, add presence event handling
  - WAHA source: `/home/openclaw/projects/waha/src/api/presence.controller.ts` — `GET /presence` returns `WAHAChatPresences[]`, `POST /presence` subscribes
  - WAHA source: `/home/openclaw/projects/waha/src/structures/presence.dto.ts` — `WAHAChatPresences`, `WAHASessionPresence` types

  **Acceptance Criteria**:
  - [ ] `GET /api/v1/presence/warung_kecantikan` returns presence data for contacts
  - [ ] Webhook receives presence updates and updates `presence_status` table
  - [ ] Conversations API includes `presence` field for each conversation

  **QA Scenarios**:
  ```
  Scenario: Get presence for session
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8001/api/v1/presence/warung_kecantikan
    Expected Result: 200 OK with JSON array of contact presences
    Failure Indicators: 404, 500, empty array (WAHA may return empty if no active chats)
    Evidence: .sisyphus/evidence/task-6-presence.json
  ```

  **Commit**: YES (group with Wave 2)

- [x] 7. **Quick Reply Templates CRUD Endpoints**

  **What to do**:
  - Create `src/oneai_reach/api/v1/templates.py` with router
  - Implement CRUD:
    - `GET /api/v1/templates` — list all templates (optionally filter by wa_number_id)
    - `POST /api/v1/templates` — create template (name, content, category, wa_number_id)
    - `PUT /api/v1/templates/{id}` — update template
    - `DELETE /api/v1/templates/{id}` — delete template
  - Use `quick_reply_templates` table from Task 1
  - Pre-seed 5 default templates: greeting, hours, pricing, thanks, follow-up
  - Register router in `main.py`

  **Must NOT do**: Don't over-engineer. Simple text templates only. No variables/interpolation in Phase A.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12 (template picker UI)
  - **Blocked By**: Task 1 (schema)

  **References**:
  - `src/oneai_reach/api/v1/products.py` — example of CRUD endpoints with Pydantic models
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py` — `quick_reply_templates` table schema

  **Acceptance Criteria**:
  - [ ] CRUD endpoints work: create, list, update, delete templates
  - [ ] Default templates pre-seeded on migration
  - [ ] Templates scoped to wa_number_id (each WA number can have its own templates)

  **QA Scenarios**:
  ```
  Scenario: Create and list templates
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/templates -H "Content-Type: application/json" -d '{"name":"Greeting","content":"Halo, terima kasih sudah menghubungi kami!","category":"greeting","wa_number_id":"warung_kecantikan"}'
      2. curl -s http://127.0.0.1:8001/api/v1/templates
    Expected Result: Template appears in list with correct fields
    Evidence: .sisyphus/evidence/task-7-templates.json
  ```

  **Commit**: YES (group with Wave 2)

- [x] 8. **Tags CRUD Endpoints + WAHA Labels Sync**

  **What to do**:
  - Create `src/oneai_reach/api/v1/tags.py` with router
  - DB tags CRUD on conversations:
    - `GET /api/v1/conversations/{id}/tags` — get tags for conversation
    - `POST /api/v1/conversations/{id}/tags` — add tags (body: `{"tags": ["hot-lead", "follow-up"]}`)
    - `DELETE /api/v1/conversations/{id}/tags/{tag}` — remove a tag
  - WAHA Labels sync:
    - `GET /api/v1/waha/{session}/labels` — list WhatsApp labels (proxied)
    - `POST /api/v1/waha/{session}/labels` — create WhatsApp label (proxied)
    - `PUT /api/v1/waha/{session}/labels/{id}` — update WhatsApp label (proxied)
    - `DELETE /api/v1/waha/{session}/labels/{id}` — delete WhatsApp label (proxied)
  - Include tags in conversations API response as `tags` array field

  **Must NOT do**: Don't auto-sync DB tags to WAHA labels. They're separate systems. Phase B can add sync if needed.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocks**: Task 12 (tag badges UI)
  - **Blocked By**: Task 1 (schema), Task 2 (proxy)

  **References**:
  - `src/oneai_reach/api/v1/conversations.py` — existing conversation endpoints
  - `src/oneai_reach/infrastructure/database/migration_crm_phase_a.py` — `conversation_tags` table schema
  - WAHA source: `/home/openclaw/projects/waha/src/api/labels.controller.ts` — labels CRUD

  **Acceptance Criteria**:
  - [ ] Can add tags to a conversation: `POST /api/v1/conversations/1/tags {"tags":["hot-lead"]}`
  - [ ] Tags appear in conversations list response
  - [ ] Can remove a tag: `DELETE /api/v1/conversations/1/tags/hot-lead`
  - [ ] WAHA labels proxy returns labels from WhatsApp

  **QA Scenarios**:
  ```
  Scenario: Add and remove tags
    Tool: Bash (curl)
    Steps:
      1. curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/tags -H "Content-Type: application/json" -d '{"tags":["hot-lead","vip"]}'
      2. curl -s http://127.0.0.1:8001/api/v1/conversations/1/tags
      3. curl -s -X DELETE http://127.0.0.1:8001/api/v1/conversations/1/tags/vip
    Expected Result: After step 2, tags array contains ["hot-lead","vip"]. After step 3, only ["hot-lead"]
    Evidence: .sisyphus/evidence/task-8-tags.txt
  ```

  **Commit**: YES (group with Wave 2)

- [x] 9. **Infinite Scroll Message History Component** (Dashboard UI)

  **What to do**:
  - Update conversations page `src/app/(dashboard)/conversations/page.tsx`
  - Replace fixed 200 message fetch with infinite scroll
  - On conversation select: call `GET /api/v1/conversations/{id}/waha-history?limit=50` to pre-load
  - On scroll to top: load more with `?before=<oldest_timestamp>`
  - Merge WAHA history messages with our `conversation_messages` (dedup by waha_message_id)
  - Show sender name, timestamp, direction indicator for each message
  - Add loading spinner at top when fetching older messages
  - Show "No more messages" when reaching the end
  - Keep existing 3s auto-refresh for new messages (bottom of chat)

  **Must NOT do**: Don't re-fetch entire history on every refresh. Only fetch deltas.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocks**: Task 13 (integration)
  - **Blocked By**: Task 4 (history API)

  **References**:
  - `src/app/(dashboard)/conversations/page.tsx` — current conversations page (508 lines, SWR, existing message rendering)
  - `src/app/(dashboard)/conversations/page.tsx` line 46-48 — existing SWR fetch of messages with 200 limit
  - `src/app/(dashboard)/conversations/page.tsx` line 40-48 — existing data fetching pattern

  **Acceptance Criteria**:
  - [ ] Opening a conversation pre-loads last 50 messages from WAHA
  - [ ] Scrolling to top loads more messages (50 at a time)
  - [ ] "No more messages" indicator when all history is loaded
  - [ ] New messages auto-appear at bottom (existing behavior preserved)

  **QA Scenarios**:
  ```
  Scenario: Infinite scroll loads history
    Tool: Playwright
    Steps:
      1. Open dashboard conversations page
      2. Click on a conversation with history
      3. Scroll to top of message area
    Expected Result: Loading spinner appears, then older messages load
    Failure Indicators: No spinner, no new messages, error toast
    Evidence: .sisyphus/evidence/task-9-infinite-scroll.png
  ```

  **Commit**: YES (group with Wave 3)

- [x] 10. **Media Upload Attachment Picker Component** (Dashboard UI)

  **What to do**:
  - Add attachment button (paperclip icon) next to the reply input in conversations page
  - Click opens file picker (accept: image/*, video/*, .pdf, .doc, .docx)
  - Show preview thumbnail for images before sending
  - On send: `POST /api/v1/conversations/{id}/send-media` with file, type, caption
  - Show sending progress indicator
  - Display sent media in message list with appropriate icon (image/video/document)
  - Drag-and-drop support for file attachment

  **Must NOT do**: Don't build a file manager. Just send media, not store/manage files.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocks**: Task 13 (integration)
  - **Blocked By**: Task 5 (media API)

  **References**:
  - `src/app/(dashboard)/conversations/page.tsx` — reply input at line 371-380
  - `src/app/(dashboard)/products/page.tsx` — existing image upload pattern in product management
  - `src/components/ui/` — shadcn/ui components (button, dialog, input)

  **Acceptance Criteria**:
  - [ ] Paperclip button visible next to reply input
  - [ ] Clicking opens file picker with correct accept types
  - [ ] Image preview shown before sending
  - [ ] Media message appears in chat after sending

  **QA Scenarios**:
  ```
  Scenario: Send image in conversation
    Tool: Playwright
    Steps:
      1. Open conversation in dashboard
      2. Click paperclip icon
      3. Select a test image file
      4. See preview thumbnail
      5. Click send button
    Expected Result: Image message appears in conversation with thumbnail
    Evidence: .sisyphus/evidence/task-10-media-send.png
  ```

  **Commit**: YES (group with Wave 3)

- [x] 11. **Presence Indicator Component** (Dashboard UI)

  **What to do**:
  - Add `GET /api/v1/presence/{session}` to conversations data fetching
  - Show online/offline dot next to contact name in conversation list
  - Online = green dot, offline = gray dot, composing = yellow dot with "typing..."
  - Show "last seen X min ago" on hover/tooltip for offline contacts
  - Auto-subscribe to presence when conversation list loads (`POST /api/v1/presence/{session}/subscribe`)
  - Update presence status every 15 seconds via polling (fallback if webhook not reliable)

  **Must NOT do**: Don't implement real-time WebSocket for presence. Polling is sufficient for Phase A.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocks**: Task 13 (integration)
  - **Blocked By**: Task 6 (presence API)

  **References**:
  - `src/app/(dashboard)/conversations/page.tsx` — conversation list rendering line 250-270
  - `src/app/(dashboard)/conversations/page.tsx` — SWR data fetching pattern

  **Acceptance Criteria**:
  - [ ] Green/gray dot visible next to contact names in conversation list
  - [ ] Hovering shows "last seen X min ago" for offline contacts
  - [ ] Presence updates within 15 seconds of change

  **QA Scenarios**:
  ```
  Scenario: Presence indicator shows
    Tool: Playwright
    Steps:
      1. Open conversations page
      2. Observe contact names in list
    Expected Result: Green or gray dot visible next to each contact name
    Evidence: .sisyphus/evidence/task-11-presence-dots.png
  ```

  **Commit**: YES (group with Wave 3)

- [x] 12. **Quick Reply Template Picker + Tag Badges** (Dashboard UI)

  **What to do**:
  - Add template picker (lightning bolt icon) next to reply input
  - Click shows dropdown of quick reply templates from `GET /api/v1/templates`
  - Selecting a template fills the reply input with template content
  - Template picker shows template name and category
  - Add tag badges on each conversation in the conversation list
  - Tags shown as small colored pills below the contact name
  - Click on tag opens filter to show only conversations with that tag
  - Add tag management: click "+" button to add tag, "x" to remove

  **Must NOT do**: Don't build a full tag CRUD UI. Simple add/remove only. Phase B for full management.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocks**: Task 13 (integration)
  - **Blocked By**: Tasks 7, 8 (templates and tags API)

  **References**:
  - `src/app/(dashboard)/conversations/page.tsx` — reply input, conversation list
  - `src/components/ui/` — shadcn/ui components (badge, dropdown, command)

  **Acceptance Criteria**:
  - [ ] Lightning bolt icon visible next to reply input
  - [ ] Clicking shows template dropdown with name and category
  - [ ] Selecting template fills reply input
  - [ ] Tags shown as colored pills on conversations
  - [ ] Can add/remove tags on conversations

  **QA Scenarios**:
  ```
  Scenario: Quick reply template picker
    Tool: Playwright
    Steps:
      1. Open conversation in dashboard
      2. Click lightning bolt icon
      3. See template list
      4. Click a template
    Expected Result: Reply input fills with template content
    Evidence: .sisyphus/evidence/task-12-template-picker.png
  ```

  **Commit**: YES (group with Wave 3)

- [x] 13. **Conversation Page Integration** (wire all components together)

  **What to do**:
  - Integrate all new components into the conversations page:
    - Infinite scroll (Task 9) replaces current 200-message fetch
    - Attachment picker (Task 10) wired to reply area
    - Presence dots (Task 11) wired to conversation list
    - Template picker (Task 12) wired to reply area
    - Tags (Task 12) wired to conversation list items
  - Add @lid display: when contact_phone contains @lid, show push_name prominently, phone number grayed out
  - Add "Open in WhatsApp" link for each conversation
  - Ensure all SWR caches are properly invalidated on mutations
  - Test the entire flow end-to-end

  **Must NOT do**: Don't redesign the conversation page layout. Add components to existing layout.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 9-12)
  - **Blocks**: Tasks 14, 15
  - **Blocked By**: Tasks 9, 10, 11, 12

  **References**:
  - `src/app/(dashboard)/conversations/page.tsx` — main conversations page (508 lines)
  - All Task 9-12 component files

  **Acceptance Criteria**:
  - [ ] All 5 features work together without conflicts
  - [ ] Page loads within 3 seconds
  - [ ] No console errors in production build

  **QA Scenarios**:
  ```
  Scenario: Full conversation flow
    Tool: Playwright
    Steps:
      1. Open conversations page
      2. See presence dots on all contacts
      3. Click a conversation
      4. Scroll up to load older messages
      5. Click paperclip, attach an image, send
      6. Click lightning, select a template, send
      7. Add a tag to the conversation
    Expected Result: All interactions work without errors
    Evidence: .sisyphus/evidence/task-13-integration.png
  ```

  **Commit**: YES (group with Wave 3)

- [x] 14. **End-to-End QA with Playwright**

  **What to do**:
  - Write Playwright tests for all Phase A features
  - Test infinite scroll: load conversation, verify 50 messages, scroll to top, verify more load
  - Test media upload: attach image, verify it sends, verify it appears in messages
  - Test presence: verify dots appear, verify update on change
  - Test templates: create template, select template, verify input fills
  - Test tags: add tag, verify badge appears, remove tag, verify badge disappears
  - Test @lid: verify @lid messages merge correctly
  - Test edge cases: empty state, no media support, offline WAHA, large messages

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocks**: Final verification
  - **Blocked By**: All implementation tasks (1-13)

  **Acceptance Criteria**:
  - [ ] All 6+ Playwright tests pass
  - [ ] No flaky tests (run 3 times, all pass)

  **QA Scenarios**:
  ```
  Scenario: Playwright test suite passes
    Tool: Bash
    Steps:
      1. npx playwright test --reporter=list
    Expected Result: All tests pass, 0 failures
    Evidence: .sisyphus/evidence/task-14-playwright-results.txt
  ```

  **Commit**: YES

- [x] 15. **Performance + Edge Case Testing**

  **What to do**:
  - Test with 500+ messages in history (infinite scroll performance)
  - Test with large files (10MB image)
  - Test with WAHA downtime (graceful error messages)
  - Test with @lid contacts that have no push_name
  - Test with duplicate messages (dedup)
  - Test concurrent access (two tabs open same conversation)
  - Verify memory usage doesn't grow unbounded with infinite scroll

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocks**: Final verification
  - **Blocked By**: All implementation tasks (1-13)

  **Acceptance Criteria**:
  - [ ] No memory leaks detected
  - [ ] 10MB file uploads succeed within 30 seconds
  - [ ] WAHA downtime shows user-friendly error, not 500

  **Commit**: YES

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — `deep`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Compare deliverables against plan.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run linter + type checks. Review all changed files for AI slop patterns. Check API error handling.

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test cross-feature integration.

---

## Commit Strategy

- **Wave 1**: `feat(crm): add Phase A DB schema + WAHA proxy + @lid merge`
- **Wave 2**: `feat(crm): add history, media, presence, templates, tags APIs`
- **Wave 3**: `feat(crm): add conversation room UI components`
- **Wave 4**: `fix(crm): QA fixes and edge cases`

---

## Success Criteria

### Verification Commands
```bash
# API health
curl -s http://127.0.0.1:8001/health  # Expected: {"status":"healthy"}

# Message history
curl -s http://127.0.0.1:8001/api/v1/conversations/1/waha-history?limit=50  # Expected: 200 OK with messages array

# Media send
curl -s -X POST -F "file=@test.jpg" http://127.0.0.1:8001/api/v1/conversations/1/send-media  # Expected: 200 OK

# Presence
curl -s http://127.0.0.1:8001/api/v1/presence/warung_kecantikan  # Expected: 200 OK with presences array

# Templates
curl -s http://127.0.0.1:8001/api/v1/templates  # Expected: 200 OK with templates array

# Tags
curl -s -X POST http://127.0.0.1:8001/api/v1/conversations/1/tags -d '{"tags":["hot-lead","follow-up"]}'  # Expected: 200 OK
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] Dashboard conversation room has infinite scroll, media upload, presence dots, template picker, tags