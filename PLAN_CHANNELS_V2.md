# Channels V2 — Independent Multi-Channel Architecture

**Status**: Planning  
**Created**: 2026-04-24  
**Scope**: Decouple channels from WhatsApp, add Telegram + Email channels, workspace-based tenant model

---

## Problem Statement

Channels (Instagram, Twitter) are currently children of WA numbers:
- Config stored at `data/channels/{platform}/{wa_number_id}/config.json`
- API routes keyed by `wa_number_id`: `/api/v1/channels/{wa_number_id}/{channel}/...`
- Dashboard requires selecting a WA number before managing channels
- `wa_number_id` serves double duty as both WA session ID and tenant context

**This prevents**: Independent channel routing, flexible mode assignment (cs/coldcall per channel), adding channels that have nothing to do with WhatsApp.

## Target Architecture

```
Workspace (tenant boundary)
  ├── Channel: "Herbal WA"     → whatsapp, cs
  ├── Channel: "BK Instagram"  → instagram, coldcall
  ├── Channel: "Outreach Email" → email, coldcall
  └── Channel: "Support TG"    → telegram, cs

Each workspace has its own:
  - Knowledge base
  - Product catalog
  - Conversation history
  - CS persona
```

---

## Phase 1: DB Schema Changes

### New Tables

```sql
-- Workspaces: the tenant boundary
CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,            -- slug: "herbal-sehat", "bk-digital"
    name TEXT NOT NULL,             -- display name
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Channels: first-class communication endpoints
CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,            -- slug: "herbal-wa", "bk-instagram"
    workspace_id TEXT NOT NULL,     -- FK to workspaces
    platform TEXT NOT NULL,         -- whatsapp, instagram, twitter, telegram, email
    label TEXT NOT NULL,            -- "Herbal Sehat WA"
    mode TEXT NOT NULL DEFAULT 'cs', -- cs, coldcall, nurture, support
    enabled INTEGER DEFAULT 1,
    connected INTEGER DEFAULT 0,
    username TEXT DEFAULT '',       -- platform username/identifier
    phone TEXT DEFAULT '',          -- for whatsapp/telegram
    config TEXT DEFAULT '{}',       -- JSON: platform-specific credentials (encrypted later)
    session_data TEXT DEFAULT '{}', -- JSON: live session info
    last_check TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);
CREATE INDEX IF NOT EXISTS idx_channels_workspace ON channels(workspace_id);
CREATE INDEX IF NOT EXISTS idx_channels_platform ON channels(platform);
CREATE INDEX IF NOT EXISTS idx_channels_mode ON channels(mode);
```

### Modified Tables (additive columns only)

```sql
-- wa_numbers: add workspace_id link
ALTER TABLE wa_numbers ADD COLUMN workspace_id TEXT;
ALTER TABLE wa_numbers ADD COLUMN channel_id TEXT;

-- conversations: add workspace_id (keep wa_number_id for backward compat)
ALTER TABLE conversations ADD COLUMN workspace_id TEXT;
ALTER TABLE conversations ADD COLUMN channel_id TEXT;

-- knowledge_base: add workspace_id
ALTER TABLE knowledge_base ADD COLUMN workspace_id TEXT;

-- products: add workspace_id
ALTER TABLE products ADD COLUMN workspace_id TEXT;

-- product_overrides: add workspace_id
-- (already has wa_number_id, just add workspace_id)

-- sales_stages: add workspace_id
ALTER TABLE sales_stages ADD COLUMN workspace_id TEXT;

-- conversation_messages: add channel_id for source tracking
ALTER TABLE conversation_messages ADD COLUMN channel_id TEXT;
```

### Migration Script

```python
def migrate_v2():
    """One-time migration: wa_numbers → workspaces + channels"""
    # 1. Create workspaces from wa_numbers
    for wa in wa_numbers:
        workspace_id = slugify(wa.label)  # "herbal-sehat"
        insert workspace(id=workspace_id, name=wa.label)
        update wa_numbers SET workspace_id=workspace_id, channel_id=workspace_id+"-wa"
        insert channel(id=workspace_id+"-wa", workspace_id=workspace_id,
                       platform="whatsapp", mode=wa.mode, label=wa.label)

    # 2. Migrate file-based channel configs to DB
    for platform_dir in data/channels/*:
        for wa_id_dir in platform_dir/*:
            config = load_json(config.json)
            workspace_id = lookup_workspace(wa_id_dir)
            insert channel(id=f"{workspace_id}-{platform_dir}",
                          workspace_id=workspace_id,
                          platform=platform_dir,
                          config=config)

    # 3. Backfill workspace_id on existing rows
    UPDATE conversations SET workspace_id = (SELECT workspace_id FROM wa_numbers WHERE id = conversations.wa_number_id)
    UPDATE knowledge_base SET workspace_id = (SELECT workspace_id FROM wa_numbers WHERE id = knowledge_base.wa_number_id)
    UPDATE products SET workspace_id = (SELECT workspace_id FROM wa_numbers WHERE id = products.wa_number_id)
```

### Data Safety
- All changes are ADDITIVE (new tables + new columns)
- No columns dropped, no tables renamed
- `wa_number_id` continues to work everywhere for backward compatibility
- Migration is idempotent (can re-run safely)

---

## Phase 2: Backend — Channel Service

### New File: `src/oneai_reach/infrastructure/messaging/channel_service.py`

Replaces `channel_config.py` file-based storage with DB-backed service.

```python
class ChannelService:
    """DB-backed channel management."""

    def list_channels(workspace_id: str = None, mode: str = None, platform: str = None) -> list[Channel]
    def get_channel(channel_id: str) -> Channel | None
    def create_channel(data: CreateChannelRequest) -> Channel
    def update_channel(channel_id: str, data: UpdateChannelRequest) -> Channel
    def delete_channel(channel_id: str) -> bool
    def test_connection(channel_id: str) -> TestResult
    def send_message(channel_id: str, recipient: str, message: str) -> bool
    def get_threads(channel_id: str, limit: int) -> list[Thread]
    def poll_inbound(channel_id: str) -> list[InboundMessage]
    def poll_all_cs() -> list[InboundMessage]  # poll all channels with mode='cs'

    # Workspace management
    def list_workspaces() -> list[Workspace]
    def get_workspace(workspace_id: str) -> Workspace | None
    def create_workspace(data: CreateWorkspaceRequest) -> Workspace
```

### Modified Files

| File | Change |
|---|---|
| `infrastructure/messaging/channels/channel_config.py` | Keep for file-based session storage, but DB is source of truth for channel identity |
| `infrastructure/messaging/channels/instagram_sender.py` | Constructor takes `channel_id` instead of `wa_number_id` |
| `infrastructure/messaging/channels/twitter_sender.py` | Same |
| `infrastructure/messaging/channels/dm_poller.py` | Uses ChannelService to find channels by mode |

---

## Phase 3: New Channel Senders

### Telegram (`src/oneai_reach/infrastructure/messaging/channels/telegram_sender.py`)

- **Library**: Telethon (MTProto user account client)
- **Why Telethon over python-telegram-bot**: Bot API requires user to message bot first. Telethon uses user account session — can DM anyone for cold outreach.
- **Auth**: Session string (Telethon session export) or phone + code
- **Install**: `pip install telethon`

```python
class TelegramSender:
    def __init__(self, channel_id: str): ...
    def send(self, username_or_phone: str, message: str) -> bool: ...
    def test_connection(self) -> TestResult: ...
    def get_threads(self, limit: int) -> list[dict]: ...
    def poll_inbound(self, limit: int) -> list[dict]: ...
```

### Email Channel (`src/oneai_reach/infrastructure/messaging/channels/email_sender.py`)

- **Strategy**: Wrap existing send chain (Brevo → Stalwart → gog → himalaya) as a channel
- **Sending**: Reuse existing `send_email()` from senders.py
- **Inbound/reply detection**: IMAP via built-in `imaplib` — check for replies to sent emails
- **Config**: `{ "from_name": "BerkahKarya", "from_email": "marketing@berkahkarya.org", "brevo_api_key": "...", "smtp_host": "...", "imap_host": "..." }`

```python
class EmailSender:
    def __init__(self, channel_id: str): ...
    def send(self, email: str, subject: str, body: str) -> bool: ...
    def test_connection(self) -> TestResult: ...
    def poll_replies(self, limit: int) -> list[dict]: ...  # IMAP inbox check
```

---

## Phase 4: API Rewrite

### New Endpoints (`src/oneai_reach/api/v1/channels.py` — full rewrite)

```
# Workspace CRUD
GET    /api/v1/workspaces                    → list workspaces
POST   /api/v1/workspaces                    → create workspace
GET    /api/v1/workspaces/{id}               → get workspace with channels

# Channel CRUD
GET    /api/v1/channels                      → list all channels (filter: workspace_id, mode, platform)
POST   /api/v1/channels                      → create channel
GET    /api/v1/channels/{id}                 → get channel details
PATCH  /api/v1/channels/{id}                 → update channel (label, mode, enabled, config)
DELETE /api/v1/channels/{id}                 → delete channel
POST   /api/v1/channels/{id}/test            → test connection
POST   /api/v1/channels/{id}/send            → send DM/message
GET    /api/v1/channels/{id}/threads         → get conversation threads
GET    /api/v1/channels/poll-cs              → poll all CS mode channels
```

### Backward Compatibility

Keep old routes as redirects:
```
GET  /api/v1/channels/{wa_number_id}          → redirects to GET /api/v1/channels?workspace_id=...
POST /api/v1/channels/{wa_number_id}/{ch}/... → maps wa_number_id to channel_id
```

---

## Phase 5: Dashboard Rewrite

### New Channels Page (`dashboard/src/app/(dashboard)/channels/page.tsx`)

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ Channels                                            [+ Add] │
├──────────────────────────────────────────────────────────────┤
│ Workspace: [Herbal Sehat ▼]                                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 💬 Herbal WA          whatsapp │ cs    ● Connected  │     │
│  │    +62 812-3456-7890              @herbal_sehat     │     │
│  │    [Disable] [Test] [Configure]                      │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 📸 BK Instagram       instagram │ coldcall  ○ Disconnected │
│  │    sessionid: [••••••••]                              │     │
│  │    [Enable] [Test] [Send DM]                          │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ 📧 Outreach Email     email │ coldcall    ● Connected│    │
│  │    marketing@berkahkarya.org                          │     │
│  │    [Disable] [Test] [Send]                            │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ ✈️ Support TG         telegram │ cs       ○ Disabled │    │
│  │    Bot token: [••••••••]                              │     │
│  │    [Enable] [Test] [Send DM]                          │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  [+ Add Channel]  → Modal: Platform, Label, Mode, Config    │
└──────────────────────────────────────────────────────────────┘
```

**Features:**
- Workspace selector at top (auto-creates default workspace)
- Per-channel card with platform icon, mode badge, connection status
- Mode toggle (cs / coldcall / nurture / support)
- Platform-specific config forms (cookies for IG/TW, session for TG, SMTP for email)
- Test connection button
- Send test DM button
- Add/remove channels dynamically

---

## Phase 6: CS Engine + Blaster Integration

### CS Engine Changes (`cs_engine_service.py`)

```python
# Before: hardcoded source_channel
async def handle_message(wa_number_id, contact_phone, message, source_channel="whatsapp"):

# After: channel-aware routing
async def handle_message(channel_id, contact_id, message):
    channel = channel_service.get_channel(channel_id)
    workspace_id = channel.workspace_id
    
    # KB and product lookup uses workspace_id
    kb_results = self.kb_search(workspace_id, message)
    products = self.product_search(workspace_id, message)
    
    # Reply goes through the same channel
    self.send_reply(channel_id, contact_id, response)
```

### Blaster Changes (`blaster.py`)

```python
# Before: hardcoded channel checks per lead column
if phone: wa_sent = send_whatsapp(phone, wa_draft)
if email: email_sent = send_email(email, subject, proposal)
if ig_handle: ig_sent = send_instagram(ig_handle, wa_draft)

# After: mode-based channel routing
coldcall_channels = channel_service.list_channels(mode="coldcall", enabled=True)
for channel in coldcall_channels:
    if channel.platform == "whatsapp" and phone:
        send_whatsapp(phone, wa_draft, session_name=channel.session_name)
    elif channel.platform == "email" and email:
        send_email(email, subject, proposal)
    elif channel.platform == "instagram" and ig_handle:
        send_instagram(ig_handle, wa_draft, channel_id=channel.id)
    elif channel.platform == "twitter" and tw_handle:
        send_twitter(tw_handle, wa_draft, channel_id=channel.id)
    elif channel.platform == "telegram" and tg_handle:
        send_telegram(tg_handle, wa_draft, channel_id=channel.id)
```

---

## Phase 7: Sidebar + Navigation

Update sidebar to add "Workspaces" section:
```
── Communication ──
  Channels
  Conversations
  
── Business ──  
  Workspaces (NEW)
  Knowledge Base
  Products
```

Or simpler: just keep "Channels" as the main entry point, with workspace selector inside.

---

## Implementation Order

| Step | Files | Est. Effort |
|---|---|---|
| 1. DB migration (workspaces + channels tables + backfill) | `infrastructure/database/migration_v2.py` | Small |
| 2. ChannelService (DB-backed CRUD) | `infrastructure/messaging/channel_service.py` | Medium |
| 3. Refactor existing senders (IG, TW) to use channel_id | `channels/instagram_sender.py`, `channels/twitter_sender.py` | Small |
| 4. Telegram sender | `channels/telegram_sender.py` | Medium |
| 5. Email channel sender | `channels/email_sender.py` | Small |
| 6. API rewrite (channels + workspaces endpoints) | `api/v1/channels.py`, `api/v1/workspaces.py` | Medium |
| 7. Dashboard channels page rewrite | `dashboard/src/app/(dashboard)/channels/page.tsx` | Medium |
| 8. CS engine + blaster wiring | `cs_engine_service.py`, `blaster.py` | Medium |
| 9. Migration script + testing | `scripts/migrate_channels_v2.py` | Small |
| 10. Visual verification + commit | — | Small |

---

## Constraints

- Port 8001 for API, 8502 for dashboard (no other ports)
- Python 3.14 (`/home/linuxbrew/.linuxbrew/bin/python3`)
- Install: `python3 -m pip install --break-system-packages`
- All open-source libraries, cookie-based auth preferred
- Schema changes ADDITIVE only (no drops)
- Systemd services, not docker-compose
- `wa_number_id` remains functional for backward compat

## Risk Assessment

| Risk | Mitigation |
|---|---|
| Breaking existing CS conversations | `wa_number_id` columns kept, new `workspace_id` added alongside |
| Data loss during migration | Migration is additive, can re-run, no data deleted |
| Telethon account ban (Telegram cold DMs) | Rate limit, spread over time, user account risk is accepted |
| Email channel complexity | Wrap existing senders.py chain, IMAP for inbound only |
| Dashboard rewrite breaks UI | Build new page, keep old as fallback until verified |
