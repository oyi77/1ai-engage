# 1ai-reach

**Cold Outreach Automation System for BerkahKarya**

Automated lead generation, enrichment, proposal drafting, and multi-channel outreach (Email + WhatsApp) with real-time email tracking.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -e .

# Start all services
systemctl --user start 1ai-reach-mcp
systemctl --user start 1ai-reach-api

# Start dashboard
cd dashboard && npm install && npm run dev
```

**Dashboard**: http://localhost:8502  
**API**: http://localhost:8000  
**Live URL**: https://reach.aitradepulse.com

---

## ✨ Features

### Core Pipeline
1. **Scraping** - Google Maps & Web via AgentCash (stableenrich)
2. **Enrichment** - Email & phone extraction via Minerva/Apollo
3. **Drafting** - AI-generated proposals and WhatsApp messages
4. **Blasting** - Multi-channel sending (Email + WhatsApp)
5. **Tracking** - Real-time email delivery, opens, clicks, bounces
6. **Follow-up** - Automated follow-up sequences
7. **CS Engine** - WhatsApp customer service with voice notes

### Email Tracking System ✅ NEW
- ✅ **Delivery Confirmation** - Know when emails reach inboxes
- ✅ **Open Tracking** - Track when recipients open emails (pixel + webhook)
- ✅ **Click Tracking** - Monitor link clicks with redirect tracking
- ✅ **Bounce Detection** - Identify invalid/bounced addresses
- ✅ **Event Audit Trail** - Complete history of all email events

**[📧 Email Tracking Documentation](EMAIL_TRACKING_COMPLETE.md)**

### Auto-Learn System
Self-improvement system that learns from conversation outcomes and optimizes responses.

---

## 📊 Dashboard (Next.js)

Primary UI running on port 8502 with real-time monitoring.

### Pages
- **Home** - System overview and service status
- **Funnel** - Lead pipeline visualization with email tracking stats
- **Conversations** - WhatsApp conversation management
- **KB** - Knowledge base editor
- **Services** - Service control (webhook, autonomous loop)
- **Auto-Learn** - Self-improvement analytics
- **Voice Settings** - Configure voice note responses
- **Pipeline Control** - Manual pipeline execution

---

## 📚 Documentation

### Getting Started
- **[Email Tracking Complete](EMAIL_TRACKING_COMPLETE.md)** - Latest feature implementation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Complete Documentation](docs/README.md)** - Full documentation index

### Architecture
- **[Architecture Overview](docs/architecture.md)** - Clean Architecture design
- **[Data Models](docs/data_models.md)** - Domain models reference
- **[API Reference](docs/api_reference.md)** - FastAPI endpoints
- **[Migration Guide](docs/migration_guide.md)** - Migration from old structure

### Email Tracking
- **[Brevo Webhook Setup](docs/BREVO_WEBHOOK_SETUP.md)** - Webhook configuration
- **[Implementation Details](docs/EMAIL_TRACKING_IMPLEMENTATION.md)** - Technical docs
- **[Feature Index](docs/EMAIL_TRACKING_INDEX.md)** - Quick reference
- **[Architecture Map](docs/EMAIL_TRACKING_MAP.md)** - System architecture

---

## 🏗️ Architecture

`1ai-reach` follows **Clean Architecture** principles:

```
┌─────────────────────────────────────────────────────────┐
│                     API / CLI Layer                      │
│              (FastAPI routes, Click commands)            │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                      │
│         (Use cases, service orchestration)               │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                         │
│        (Business logic, models, interfaces)              │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                     │
│     (External APIs, database, messaging, logging)        │
└─────────────────────────────────────────────────────────┘
```

**Key principles:**
- Dependencies flow inward (outer layers depend on inner layers)
- Domain layer has zero external dependencies
- Repository pattern abstracts data access
- Dependency injection for loose coupling
- Pydantic models for type safety and validation

See [Architecture Overview](docs/architecture.md) for detailed design documentation.

## Directory Structure

**New Structure** (Clean Architecture):
```
src/oneai_reach/
├── domain/              # Business logic (pure)
│   ├── models/          # Pydantic models (Lead, Conversation, Message, Proposal, KB)
│   ├── services/        # Business rules and domain logic
│   ├── repositories/    # Abstract data access interfaces
│   └── exceptions.py    # Custom exceptions with error codes
├── application/         # Use cases & orchestration
│   ├── outreach/        # Pipeline services (scraper, enricher, generator, blaster)
│   ├── customer_service/# CS engine, conversation tracking, analytics
│   ├── voice/           # Voice pipeline (STT, TTS, audio processing)
│   └── agents/          # Agent orchestration (strategy, closer, autonomous loop)
├── infrastructure/      # External integrations
│   ├── database/        # SQLite repository implementations
│   ├── external/        # API clients (BrainClient, WAHAClient, AgentCash)
│   ├── llm/             # LLM integration (Claude, Gemini, Oracle)
│   ├── messaging/       # Email/WhatsApp senders with fallback chains
│   └── logging/         # Structured JSON logging with correlation IDs
├── api/                 # HTTP interface
│   ├── v1/              # API endpoints (pipeline, conversations, KB)
│   ├── webhooks/        # Webhook handlers (WAHA, CAPI)
│   ├── middleware.py    # Auth, rate limiting, CORS, logging
│   └── main.py          # FastAPI application
├── cli/                 # CLI interface
│   └── main.py          # Click commands (7 command groups)
└── config/              # Configuration
    └── settings.py      # Pydantic Settings (14 config groups)
```

**Legacy Structure** (backward compatible):
- `dashboard/`: Next.js frontend (TypeScript + React)
- `scripts/`: Python modules (now shims to new CLI)
- `data/`: Lead databases (`leads.csv`)
- `proposals/`: Generated proposals
- `logs/`: Execution logs

## Voice Features (WhatsApp Customer Service)

The system supports voice note replies for WhatsApp CS mode. When enabled, customers can send voice notes and receive AI-generated voice responses.

### Voice Pipeline

```
Voice Input (OGG) → faster-whisper (STT) → cs_engine (AI response) → ChatterBox TTS (TTS) → WAHA (voice note)
```

### Configuration

Voice settings are configurable per WA number via the dashboard at `/voice-settings` or via API:

```
GET  /api/voice-config/<session_name>  → get voice config
PATCH /api/voice-config/<session_name> → update voice config
```

### Voice Settings

| Setting | Options | Description |
|---|---|---|
| `voice_enabled` | true/false | Enable/disable voice replies |
| `voice_reply_mode` | auto/voice_only/text_only | When to use voice vs text |
| `voice_language` | ms/id/en | TTS response language |

Default language is Indonesian (Bahasa Indonesia).

## Usage (via Telegram)
Tell Vilona:
- "Scrape leads for [Niche] in [City]"
- "Enrich our current leads"
- "Generate proposals for the leads"
- "Blast the leads"

## Agent Control (MCP)

`1ai-reach` now exposes an MCP control plane so other AI agents can inspect and operate the backend safely.

### Install MCP dependencies
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

### Start MCP over stdio
```bash
python3 mcp_server.py --transport stdio
```

### Start MCP over HTTP
```bash
python3 mcp_server.py --transport http --host 127.0.0.1 --port 8765
```

HTTP MCP endpoint:
```text
http://127.0.0.1:8765/mcp
```

### Main MCP capabilities
- Read funnel state and lead records
- Read control-plane audit history
- Inspect WAHA / hub brain integrations
- Preview autonomous decisions
- Run individual pipeline stages
- Start/stop/list long-running background jobs
- Send live test email / WhatsApp messages
- Enforce DB-backed job tracking and singleton loop ownership

See `SKILL.md` for the agent workflow and tool inventory.

Or run the orchestrator:
```bash
python3 scripts/orchestrator.py "Coffee Shop in Jakarta"
```

## Admin Control
Admin can monitor progress by asking Vilona for a "status update on 1ai-reach".
Vilona will report:
- Total leads found
- Leads enriched
- Proposals drafted
- Messages sent
