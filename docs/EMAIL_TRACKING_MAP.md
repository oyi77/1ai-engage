# Email Tracking & Delivery Infrastructure Map
## 1ai-reach Cold Outreach System

**Generated:** 2026-04-21
**Project:** /home/openclaw/projects/1ai-reach

---

## EXECUTIVE SUMMARY

The 1ai-reach system has **NO native email open/click tracking** implemented. Email delivery is tracked at the **send-level only** via fallback chain status. Reply detection happens through **Gmail inbox polling** (gog CLI) and **WhatsApp webhook** integration, not email tracking pixels or webhooks.

### Current Tracking Capabilities:
- ✅ Email sent confirmation (via fallback chain)
- ✅ Email reply detection (Gmail inbox polling)
- ✅ WhatsApp message delivery status (WAHA webhooks)
- ✅ WhatsApp read receipts (WAHA status webhook)
- ❌ Email open tracking (no pixel/beacon)
- ❌ Email click tracking (no link rewriting)
- ❌ Email bounce handling (no webhook integration)
- ❌ Email engagement metrics (no analytics)

---

## 1. EMAIL DELIVERY INFRASTRUCTURE

### 1.1 Email Sender (Fallback Chain)
**File:** `src/oneai_reach/infrastructure/messaging/email_sender.py`

**Fallback Order:**
1. **Brevo HTTP API** (Primary)
   - 300/day free tier
   - Trusted IP whitelisting
   - Returns `messageId` on success
   - Status codes: 200, 201

2. **Stalwart SMTP** (Fallback 1)
   - Host: `settings.email.smtp_host`
   - Port: `settings.email.smtp_port`
   - Auth: `settings.email.smtp_user` / `settings.email.smtp_password`
   - From: `settings.email.smtp_from`

3. **gog CLI** (Fallback 2)
   - Gmail via `gog gmail send`
   - Env: `GOG_KEYRING_PASSWORD`, `GOG_ACCOUNT`
   - Account: `settings.gmail.account`

4. **himalaya CLI** (Fallback 3)
   - IMAP/SMTP via `himalaya template send`
   - No auth required (uses system keyring)

5. **Queue to File** (Last Resort)
   - Path: `logs/email_queue.log`
   - Format: Plain text log
   - Manual review required

**Key Methods:**
```python
send(email, subject, body) -> bool
_send_via_brevo(email, subject, body) -> bool
_send_via_stalwart(email, subject, body) -> bool
_send_via_gog(email, subject, body) -> bool
_send_via_himalaya(email, subject, body) -> bool
_send_via_queue(email, subject, body) -> bool
_make_html_body(body) -> str  # Branded HTML template
```

**HTML Email Template:**
- BerkahKarya branding (logo, green header #1a7a4a)
- Responsive design (600px width)
- Unsubscribe footer (Indonesian: "Jika Anda tidak ingin menerima email ini, balas dengan kata 'berhenti'")
- Logo URL: `https://raw.githubusercontent.com/oyi77/1ai-reach/master/assets/logo.svg`

**Tracking:** ❌ No tracking pixels, no open/click detection

---

### 1.2 Message Queue (Rate Limiting & Retry)
**File:** `src/oneai_reach/infrastructure/messaging/message_queue.py`

**Purpose:** Manage email queue with status tracking and retry logic

**Queue Schema (JSON):**
```json
{
  "id": 0,
  "type": "email",
  "recipient": "prospect@company.com",
  "subject": "Proposal",
  "body": "...",
  "status": "pending|sent|failed",
  "error": "error message if failed",
  "created_at": "2026-04-21T06:44:31.812Z",
  "updated_at": "2026-04-21T06:44:31.812Z",
  "retry_count": 0
}
```

**Key Methods:**
```python
add(message_type, recipient, subject, body, status, error) -> int
get_pending() -> List[Dict]  # pending or failed messages
mark_sent(message_id) -> bool
mark_failed(message_id, error) -> bool
get_stats() -> Dict[status -> count]
clear_sent() -> int  # Remove sent messages
```

**Tracking:** ❌ No delivery confirmation from email providers, only local status

---

## 2. REPLY DETECTION INFRASTRUCTURE

### 2.1 Reply Tracker Service
**File:** `src/oneai_reach/application/outreach/reply_tracker_service.py`

**Purpose:** Detect email and WhatsApp replies to contacted leads

**Email Reply Detection:**
1. **Primary:** `gog gmail search` (Gmail CLI)
   - Query: `in:inbox -from:{gmail_account}`
   - Fallback query: `in:inbox`
   - Extracts sender email from `from` field
   - Stores reply text (first 2000 chars)

2. **Fallback:** `himalaya envelope list` (IMAP CLI)
   - JSON output parsing
   - Extracts sender address and body

**WhatsApp Reply Detection:**
1. **Primary:** WAHA HTTP API
   - Endpoint: `GET {base_url}/api/chats`
   - Params: `session`, `limit=100`
   - Extracts: `chat.id`, `lastMessage.body`, `lastMessage.id`
   - Deduplication: `waha_message_id` check in DB

2. **Fallback:** Direct WAHA session list
   - Endpoint: `GET {base_url}/api/sessions`
   - Filters: `status == "WORKING"`

**Key Methods:**
```python
check_replies(df, update_lead_fn, ...) -> int
_gog_search(query) -> List[dict]
_extract_sender_email(thread) -> str
_waha_targets() -> List[Tuple[name, url, headers]]
_waha_sessions(base_url, headers, get_wa_numbers_fn) -> List[dict]
_is_waha_msg_processed(waha_message_id, db_connect_fn) -> bool
_check_replies_waha(...) -> None
_check_replies_himalaya(...) -> None
_route_waha_message(mode, ...) -> None  # Routes to CS/warmcall/cold
_handle_cold_reply(digits, body, ...) -> None
```

**Lead Status Update on Reply:**
```python
df.at[index, "status"] = "replied"
df.at[index, "replied_at"] = datetime.now(timezone.utc).isoformat()
update_lead_fn(lead_id, reply_text=reply_text)
```

**Tracking:** ✅ Email replies via Gmail polling, ✅ WhatsApp replies via WAHA API

---

## 3. WEBHOOK INFRASTRUCTURE

### 3.1 WAHA Webhook (WhatsApp)
**File:** `src/oneai_reach/api/webhooks/waha.py`
**Endpoint:** `POST /api/v1/webhooks/waha/message`

**Events Handled:**
- `message` / `message.any` - Inbound WhatsApp messages
- `status` - Message delivery/read status updates

**Message Webhook Payload:**
```python
{
  "event": "message",
  "session": "session_name",
  "payload": {
    "from": "62812345678@c.us",
    "chatId": "62812345678@c.us",
    "body": "Message text",
    "type": "chat|image|video|document|audio|ptt",
    "fromMe": false,
    "id": "waha_message_id_xyz",
    "media": {"url": "..."}
  }
}
```

**Processing:**
1. Deduplication: `_processed_messages` set (in-memory, max 1000)
2. Filters: Skip `fromMe`, group messages (`@g.us`), unsupported types
3. Rate limiting: `_CONVERSATION_MESSAGE_COUNTS` (max 50 messages/conversation)
4. Voice handling: `process_inbound_voice()` if enabled
5. CS Engine: `cs_engine.handle_inbound_message()` for auto-reply
6. Message storage: `add_conversation_message()` to DB

**Status Webhook Payload:**
```python
{
  "event": "status",
  "session": "session_name",
  "data": {...}
}
```

**Tracking:** ✅ Message delivery status via WAHA webhook

---

### 3.2 CAPI Webhook (Meta Conversions API)
**File:** `src/oneai_reach/api/webhooks/capi.py`
**Endpoint:** `POST /api/v1/webhooks/capi/lead`

**Purpose:** Track lead events to Meta for attribution

**Payload:**
```python
{
  "phone": "62812345678",
  "event_type": "lead|purchase|atc"
}
```

**Events:**
- `lead` - Lead form submission
- `purchase` - Purchase conversion
- `atc` - Add to cart

**Tracking:** ✅ Lead events to Meta Conversions API (not email-specific)

---

## 4. DATABASE SCHEMA

### 4.1 Leads Table
**File:** `src/oneai_reach/infrastructure/database/sqlite_lead_repository.py`

**Tracked Fields:**
```sql
CREATE TABLE leads (
  id TEXT PRIMARY KEY,
  email TEXT,
  phone TEXT,
  internationalPhoneNumber TEXT,
  status TEXT,  -- new|enriched|draft_ready|needs_revision|reviewed|contacted|followed_up|replied|meeting_booked|won|lost|cold|unsubscribed
  contacted_at TEXT,  -- Timestamp when contacted
  followup_at TEXT,   -- Timestamp of follow-up
  replied_at TEXT,    -- Timestamp of reply
  reply_text TEXT,    -- Full reply message (first 2000 chars)
  review_score TEXT,  -- Proposal review score
  review_issues TEXT, -- Review issues
  created_at TEXT,
  updated_at TEXT
)
```

**Tracking:** ✅ Email sent timestamp, ✅ Reply timestamp, ✅ Reply text

---

### 4.2 Conversations Table
**File:** `src/oneai_reach/infrastructure/database/sqlite_conversation_repository.py`

**Schema:**
```sql
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wa_number_id TEXT,
  contact_phone TEXT NOT NULL,
  contact_name TEXT,
  lead_id TEXT,
  engine_mode TEXT,  -- cs|cold|manual
  status TEXT,       -- active|resolved|escalated|cold
  manual_mode INTEGER,
  test_mode INTEGER,
  last_message_at TEXT,
  message_count INTEGER,
  created_at TEXT,
  updated_at TEXT
)
```

**Tracking:** ✅ WhatsApp conversation metrics

---

### 4.3 Conversation Messages Table
**File:** `scripts/state_manager.py`

**Schema:**
```sql
CREATE TABLE conversation_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id INTEGER,
  direction TEXT,           -- in|out
  message_text TEXT,
  message_type TEXT,        -- text|voice|image|document|video|audio|sticker|location|contact
  waha_message_id TEXT,     -- WAHA webhook message ID (for deduplication)
  timestamp TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id)
)
```

**Tracking:** ✅ Message direction, ✅ WAHA message ID for deduplication

---

## 5. MISSING EMAIL TRACKING FEATURES

### 5.1 Email Open Tracking
**Status:** ❌ NOT IMPLEMENTED

**What's Missing:**
- No tracking pixel in HTML emails
- No beacon/1x1 GIF
- No open event webhook
- No open timestamp recording

**Why:**
- Brevo API doesn't expose open tracking in free tier
- No custom webhook integration for email provider events
- No pixel tracking infrastructure

**To Implement:**
1. Add tracking pixel to `_make_html_body()`:
   ```html
   <img src="https://track.example.com/open/{lead_id}/{message_id}" width="1" height="1" alt="" />
   ```
2. Create webhook endpoint: `POST /api/v1/webhooks/email/open`
3. Add `email_opened_at` field to leads table
4. Store pixel tracking events in DB

---

### 5.2 Email Click Tracking
**Status:** ❌ NOT IMPLEMENTED

**What's Missing:**
- No link rewriting
- No click event tracking
- No click timestamp recording
- No engagement metrics

**Why:**
- No URL rewriting middleware
- No click tracking service
- No analytics dashboard

**To Implement:**
1. Create link rewriter: `rewrite_links_for_tracking(body, lead_id)`
2. Create webhook endpoint: `POST /api/v1/webhooks/email/click`
3. Add `email_clicked_at`, `email_click_count` to leads table
4. Store click events with URL and timestamp

---

### 5.3 Email Bounce Handling
**Status:** ❌ NOT IMPLEMENTED

**What's Missing:**
- No bounce webhook integration
- No bounce classification (hard/soft)
- No automatic unsubscribe on hard bounce
- No bounce rate tracking

**Why:**
- Brevo API doesn't expose bounce events in free tier
- No webhook handler for bounce events
- No bounce status field in leads table

**To Implement:**
1. Configure Brevo webhook: `POST /api/v1/webhooks/email/bounce`
2. Add `bounce_status` field to leads table (hard|soft|none)
3. Auto-mark as `unsubscribed` on hard bounce
4. Track bounce rate in analytics

---

### 5.4 Email Engagement Metrics
**Status:** ❌ NOT IMPLEMENTED

**What's Missing:**
- No engagement scoring
- No analytics dashboard
- No engagement trends
- No A/B testing infrastructure

**Why:**
- No centralized tracking data
- No analytics service
- No dashboard UI

**To Implement:**
1. Create `EmailEngagement` model with: opens, clicks, replies, bounces
2. Create analytics service: `calculate_engagement_score(lead_id)`
3. Add dashboard page: `/analytics/email-engagement`
4. Track metrics: open rate, click rate, reply rate, bounce rate

---

## 6. CURRENT TRACKING FLOW

### 6.1 Email Send Flow
```
blaster_service.py
  ↓
send_email_fn(email, subject, body)
  ↓
email_sender.EmailSender.send()
  ├─ Try Brevo API
  ├─ Try Stalwart SMTP
  ├─ Try gog CLI
  ├─ Try himalaya CLI
  └─ Queue to file
  ↓
Lead.contacted_at = now
Lead.status = "contacted"
```

**Tracking:** ✅ Send confirmation, ❌ No delivery confirmation

---

### 6.2 Reply Detection Flow
```
reply_tracker_service.check_replies()
  ├─ Email replies:
  │  ├─ gog gmail search "in:inbox"
  │  ├─ Extract sender email
  │  └─ himalaya fallback
  │
  └─ WhatsApp replies:
     ├─ WAHA API: GET /api/chats
     ├─ Extract chat_id, lastMessage.body
     ├─ Dedup: waha_message_id check
     └─ Route to CS/warmcall/cold
  ↓
Lead.replied_at = now
Lead.reply_text = message_text
Lead.status = "replied"
```

**Tracking:** ✅ Reply detection, ✅ Reply text storage

---

### 6.3 WhatsApp Delivery Flow
```
WAHA Webhook: POST /api/v1/webhooks/waha/status
  ↓
Event: "status"
  ├─ delivery: Message delivered to phone
  ├─ read: Message read by customer
  └─ error: Delivery failed
  ↓
conversation_messages table
  ├─ waha_message_id (for dedup)
  ├─ timestamp
  └─ direction (in|out)
```

**Tracking:** ✅ WhatsApp delivery status, ✅ Read receipts

---

## 7. CONFIGURATION

### 7.1 Email Settings
**File:** `src/oneai_reach/config/settings.py`

```python
class EmailSettings(BaseSettings):
    brevo_api_key: str = ""
    smtp_host: str = "smtp.stalwart.org"
    smtp_port: int = 587
    smtp_user: str = "marketing@berkahkarya.org"
    smtp_password: str = ""
    smtp_from: str = "BerkahKarya <marketing@berkahkarya.org>"
```

### 7.2 Gmail Settings
```python
class GmailSettings(BaseSettings):
    account: str = "moliangellina@gmail.com"
    keyring_password: str = ""
```

### 7.3 WAHA Settings
```python
class WAHASettings(BaseSettings):
    url: str = "http://5.189.138.144:3000"
    direct_url: str = ""
    api_key: str = "321"
    direct_api_key: str = ""
    session: str = "default"
    webhook_path: str = "/webhook/waha"
    webhook_secret: str = ""
```

---

## 8. INTEGRATION POINTS

### 8.1 Blaster Service
**File:** `src/oneai_reach/application/outreach/blaster_service.py`

```python
def blast_leads(df, send_email_fn, send_whatsapp_fn):
    for lead in df:
        email_sent = send_email_fn(lead.email, subject, body)
        wa_sent = send_whatsapp_fn(lead.phone, wa_message)
        
        if wa_sent or email_sent:
            lead.status = "contacted"
            lead.contacted_at = now
```

---

### 8.2 Converter Service
**File:** `src/oneai_reach/application/outreach/converter_service.py`

Converts `replied` leads to `meeting_booked`:
- Sends meeting invite email
- Creates PaperClip issue
- Triggers n8n workflow

---

## 9. RECOMMENDATIONS

### Priority 1: Email Open Tracking
- Add tracking pixel to HTML template
- Create webhook endpoint for open events
- Store `email_opened_at` in leads table
- Implement open rate analytics

### Priority 2: Email Click Tracking
- Implement link rewriter
- Create click webhook endpoint
- Track click events with URL
- Build engagement dashboard

### Priority 3: Bounce Handling
- Integrate Brevo bounce webhook
- Auto-unsubscribe on hard bounce
- Track bounce rate
- Alert on high bounce rate

### Priority 4: Email Engagement Scoring
- Calculate engagement score (opens + clicks + replies)
- Segment leads by engagement level
- Optimize follow-up timing based on engagement
- A/B test subject lines and content

---

## 10. FILES SUMMARY

| File | Purpose | Tracking |
|------|---------|----------|
| `email_sender.py` | Email delivery (5-method fallback) | ✅ Send status |
| `message_queue.py` | Queue management & retry | ✅ Queue status |
| `reply_tracker_service.py` | Email/WA reply detection | ✅ Reply detection |
| `waha.py` | WhatsApp webhook handler | ✅ WA delivery/read |
| `capi.py` | Meta Conversions API webhook | ✅ Lead events |
| `sqlite_lead_repository.py` | Lead persistence | ✅ Timestamps |
| `sqlite_conversation_repository.py` | Conversation persistence | ✅ Message count |
| `state_manager.py` | Message storage | ✅ WAHA message ID |

---

## 11. NEXT STEPS

1. **Audit current email delivery** - Check Brevo logs for actual delivery rates
2. **Implement open tracking** - Add pixel to HTML template
3. **Add click tracking** - Implement link rewriter
4. **Create analytics dashboard** - Visualize engagement metrics
5. **Set up bounce handling** - Integrate Brevo bounce webhook
6. **Build engagement scoring** - Segment leads by engagement level

