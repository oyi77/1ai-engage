<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-06 | Updated: 2026-05-06 -->

# scripts

## Purpose
Legacy orchestration engine containing 54+ Python modules that drive the core outreach pipeline. These scripts implement lead scraping, enrichment, AI proposal generation, multi-channel blasting, reply tracking, customer service, voice calls, and self-improvement loops. Originally standalone scripts, now wrapped by the Clean Architecture backend in `src/oneai_reach/`.

## Key Files
| File | Description |
|------|-------------|
| `orchestrator.py` | Master workflow controller — sequences the full outreach pipeline |
| `autonomous_loop.py` | Autonomous agent loop — runs continuous outreach cycles |
| `config.py` | Configuration management — loads env vars and settings |
| `llm_client.py` | LLM provider integration — OpenAI/Azure/etc. |
| `brain_client.py` | Brain/memory client — connects to 1ai-hub for shared memory |
| `state_manager.py` | SQLite state persistence for pipeline runs |
| `mcp_server.py` | MCP server for agent control (backward compat entry point) |
| `webhook_server.py` | Webhook handlers for external event processing |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `data/` | SQLite databases, JSON knowledge bases used by scripts |
| `migrations/` | Database migration scripts for script-managed tables |

## Pipeline Modules by Category

### Lead Processing (7 modules)
| File | Description |
|------|-------------|
| `leads.py` | Lead management — CRUD, querying, dedup |
| `lead_scorer.py` | Lead scoring — fit/intent/engagement signals |
| `scraper.py` | Web scraping — Google Maps, directories, websites |
| `gmaps_client.py` | Google Maps API — business search and data extraction |
| `vibe_scraper.py` | Vibe-based scraping — context-aware lead discovery |
| `enricher.py` | Lead enrichment — email finding, company data, social profiles |
| `researcher.py` | Deep research — company profiling, pain point discovery |

### Content Generation (4 modules)
| File | Description |
|------|-------------|
| `generator.py` | AI content generation — proposals, emails, messages |
| `converter.py` | Format conversion — HTML/Markdown/Plain text |
| `reviewer.py` | Content review — quality checks, compliance screening |
| `kb_manager.py` | Knowledge base management — CRUD, search, import/export |

### Outreach Delivery (5 modules)
| File | Description |
|------|-------------|
| `blaster.py` | Email/SMS blast engine — batch delivery with rate limiting |
| `senders.py` | Multi-channel senders — email, WhatsApp, SMS adapters |
| `wa_manager.py` | WhatsApp management — session control, message sending via WAHA |
| `reply_tracker.py` | Reply tracking — response detection and threading |
| `capi_tracker.py` | CAPI (Conversions API) tracking — delivery/open/click events |

### Customer Service (6 modules)
| File | Description |
|------|-------------|
| `cs_engine.py` | Customer service engine — chat handling, escalation |
| `cs_analytics.py` | CS analytics — satisfaction, resolution metrics |
| `cs_outcomes.py` | Outcome tracking — conversions, escalations, closes |
| `cs_self_improve.py` | Self-improvement — learns from CS conversations |
| `cs_learn.py` | Learning system — knowledge extraction from interactions |
| `cs_playbook.py` | Playbook management — automated response rules |

### Sales Agents (5 modules)
| File | Description |
|------|-------------|
| `strategy_agent.py` | Strategy agent — plans outreach approach |
| `closer_agent.py` | Closer agent — handles negotiation and closing |
| `warmcall_engine.py` | Warm call engine — voice-based outreach |
| `flosia_sales_engine.py` | Flosia sales engine — specialized sales flow |
| `service_detector.py` | Service detector — identifies target services |

### Voice & Audio (3 modules)
| File | Description |
|------|-------------|
| `voice_pipeline.py` | Voice pipeline — orchestrates STT/TTS/call flow |
| `stt_engine.py` | Speech-to-text engine — audio transcription |
| `tts_engine.py` | Text-to-speech engine — audio generation |

### Infrastructure & Support (22 modules)
| File | Description |
|------|-------------|
| `n8n_client.py` | n8n workflow automation client |
| `sheets_sync.py` | Google Sheets synchronization |
| `guard_checker.py` | Safety guard — compliance and quality checks |
| `conversation_guard.py` | Conversation guard — prevents off-topic/harmful exchanges |
| `conversation_tracker.py` | Conversation state tracking |
| `conversation_cleanup.py` | Conversation data cleanup/GDPR |
| `health_monitor.py` | Health monitoring for all services |
| `ab_testing.py` | A/B testing for copy optimization |
| `followup.py` | Follow-up sequence management |
| `capi_tracker.py` | Conversion API tracking |
| `audio_utils.py` | Audio processing utilities |
| `utils.py` | Shared utility functions |
| `deploy_fixes.sh` | Deployment fix scripts |
| `start_services.sh` | Service startup script |
| `setup_systemd.sh` | Systemd service installation |
| `ecosystem.config.js` | PM2 process management |
| `kb_import_export.py` | Knowledge base import/export |
| `migrate_csv_to_sqlite.py` | CSV → SQLite migration |
| `voice_config.py` | Voice call configuration |
| `lead_scorer.py` | Lead scoring algorithms |
| `cs_learn_cli.py` | CLI for CS learning system |
| `service_detector.py` | Service detection for leads |

## For AI Agents

### Working In This Directory
- These are **active legacy scripts** — still used in production alongside the Clean Architecture backend
- All scripts use raw `sqlite3` for database access (no ORM)
- Configuration via environment variables through `config.py`
- `brain_client.py` connects to 1ai-hub on localhost:9099
- `wa_manager.py` connects to WAHA API for WhatsApp messaging
- Scripts can be run standalone or orchestrated by `orchestrator.py`
- MCP server in `mcp_server.py` provides agent control interface

### Testing Requirements
- Most scripts lack unit tests — rely on integration testing
- Test with small data sets in `data/` directory
- Never run blast/scripts against real contacts without explicit approval

### Common Patterns
- Each script is self-contained with its own DB connection via `sqlite3`
- Logging goes to stdout + `logs/` directory
- Error handling: try/except with structured logging
- LLM calls via `llm_client.py` with retry logic
- Rate limiting built into sender modules

## Dependencies

### Internal
- `brain_client.py` → `1ai-hub/` (shared brain/memory)
- `wa_manager.py` → `waha/` (WhatsApp API)
- `config.py` → `.env` (environment configuration)

### External
- Python 3.10+
- sqlite3 (stdlib), requests, beautifulsoup4
- OpenAI / Azure OpenAI (LLM)
- Google Maps API, Google Sheets API
- n8n workflow engine (optional)

<!-- MANUAL: Custom project notes can be added below -->