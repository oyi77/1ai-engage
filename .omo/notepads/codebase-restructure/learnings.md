# Task 1: Package Structure Skeleton - Learnings

## Completed
- Created Clean Architecture directory layout under `src/oneai_reach/`
- All 21 directories have `__init__.py` files (verified)
- Updated `pyproject.toml` with proper package configuration: `packages = [{include = "oneai_reach", from = "src"}]`
- Package import verification passed

## Directory Structure Created
```
src/oneai_reach/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── repositories/
├── application/
│   ├── __init__.py
│   ├── outreach/
│   ├── customer_service/
│   ├── agents/
│   └── voice/
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   ├── external/
│   ├── llm/
│   ├── messaging/
│   └── logging/
├── api/
│   ├── __init__.py
│   ├── v1/
│   └── webhooks/
├── cli/
│   └── __init__.py
└── config/
    └── __init__.py
```

## Key Points
- All 21 `__init__.py` files created successfully
- Package is importable: `import oneai_reach` works with `sys.path.insert(0, 'src')`
- No existing code moved or modified - skeleton only
- Ready for Task 2: Domain models migration

# Task 2: Pydantic Settings Configuration - Learnings

## Completed
- Created `src/oneai_reach/config/settings.py` with 14 typed settings classes
- All constants from `scripts/config.py` migrated to Pydantic BaseSettings
- Environment variable validation with proper type hints
- `get_settings()` singleton with `@lru_cache()` for performance
- `.env.example` created with all 60+ documented variables
- Backward compatibility: `scripts/config.py` now imports from new settings
- Settings load verification: PASSED
- Backward compatibility verification: PASSED
- Validation error handling: PASSED

## Settings Classes Created
1. **DatabaseSettings** - File paths (leads_file, db_file, data_dir, research_dir, proposals_dir, logs_dir)
2. **PipelineSettings** - Loop execution (loop_sleep_seconds, min_new_leads_threshold)
3. **LLMSettings** - Model selection (generator_model, reviewer_model)
4. **BookingSettings** - Links (payment_link, calendly_link)
5. **EmailSettings** - Brevo + Stalwart SMTP (brevo_api_key, smtp_host, smtp_port, smtp_user, smtp_password)
6. **GmailSettings** - Gmail + Sheets (account, keyring_password, sheet_id)
7. **HubSettings** - BerkahKarya Hub (url, api_key)
8. **WAHASettings** - WhatsApp API (url, direct_url, api_key, direct_api_key, session, own_number, webhook_path, webhook_secret)
9. **CustomerServiceSettings** - CS engine (mcp_base_url, reply_delay_seconds, max_replies_per_minute, escalation_telegram, default_persona, max_turns)
10. **N8nSettings** - n8n workflows (base, meeting_wf, webhook_url)
11. **TelegramSettings** - Telegram alerts (bot_token, chat_id)
12. **ExternalAPISettings** - External APIs (google_api_key, aitradepulse_api_key)
13. **PaperClipSettings** - PaperClip OS (url, company_id, agent_cmo)
14. **ScraperSettings** - Scraper config (aggregator_domains set, default_verticals list)

## Key Implementation Details
- Each settings class uses `env_prefix` for namespace isolation (e.g., `DB_`, `SMTP_`, `WAHA_`)
- Root `Settings` class has `extra = "ignore"` to handle environment variables not mapped to fields
- Environment variables loaded from `.env` file automatically via Pydantic
- Type validation: integers, strings, booleans, sets, lists all validated
- Singleton pattern via `@lru_cache(maxsize=1)` on `get_settings()`

## Backward Compatibility Strategy
- `scripts/config.py` now imports from `oneai_reach.config.settings`
- All legacy constants (LEADS_FILE, HUB_URL, WAHA_API_KEY, etc.) still available
- Existing code can continue using: `from scripts.config import LEADS_FILE`
- New code should use: `from oneai_reach.config.settings import get_settings`
- Path conversion: Settings returns strings, config.py converts to Path objects where needed

## Environment Variable Naming Convention
- Prefix format: `{SECTION}_{FIELD_NAME}` (uppercase, snake_case)
- Examples:
  - `DB_LEADS_FILE` → DatabaseSettings.leads_file
  - `SMTP_PASSWORD` → EmailSettings.smtp_password
  - `WAHA_API_KEY` → WAHASettings.api_key
  - `CS_REPLY_DELAY_SECONDS` → CustomerServiceSettings.reply_delay_seconds

## Verification Results
✓ Settings load successfully with all 14 configuration groups
✓ Backward compatibility: legacy imports work correctly
✓ Type validation: invalid types rejected with ValidationError
✓ Singleton caching: `get_settings()` returns cached instance
✓ Environment variable override: .env values loaded correctly

## Files Created/Modified
- Created: `src/oneai_reach/config/settings.py` (315 lines)
- Created: `.env.example` (60+ documented variables)
- Modified: `scripts/config.py` (now imports from settings, 95 lines)
- Evidence: `.sisyphus/evidence/task-2-settings-load.txt`
- Evidence: `.sisyphus/evidence/task-2-validation-error.txt`

## Next Steps
- Task 3: Domain models migration (leads, proposals, conversations)
- Task 4: Repository pattern implementation
- Task 5: Application service layer

# Task 3: Domain Models with Pydantic - Learnings

## Completed
- Created 5 Pydantic domain models with full validation
- All models support `from_attributes=True` for ORM compatibility
- Enums created for status values and types
- Field validation: email format, phone normalization, score ranges, priority ranges
- Computed properties for business logic
- Evidence files created with validation tests

## Models Created

### 1. Lead Model (`src/oneai_reach/domain/models/lead.py`)
- **Fields**: id, displayName, email, phone, internationalPhoneNumber, formattedAddress, websiteUri, linkedin, primaryType, type, source, status, contacted_at, followup_at, replied_at, research, review_score, review_issues, reply_text, created_at, updated_at
- **Enum**: LeadStatus (13 stages: new, enriched, draft_ready, needs_revision, reviewed, contacted, followed_up, replied, meeting_booked, won, lost, cold, unsubscribed)
- **Validation**: 
  - Email format via EmailStr
  - Phone normalization: 081234567890 → +6281234567890
  - URL validation: adds https:// if missing
- **Computed Properties**: is_warm, is_cold, days_since_contact, days_since_reply, needs_followup, is_replied

### 2. Conversation Model (`src/oneai_reach/domain/models/conversation.py`)
- **Fields**: id, wa_number_id, contact_phone, contact_name, lead_id, engine_mode, status, manual_mode, test_mode, last_message_at, message_count, created_at, updated_at
- **Enums**: 
  - ConversationStatus (active, resolved, escalated, cold)
  - EngineMode (cs, cold, manual)
- **Computed Properties**: is_active, is_escalated, hours_since_last_message, is_stale (>48h), is_cold_lead

### 3. Message Model (`src/oneai_reach/domain/models/message.py`)
- **Fields**: id, conversation_id, waha_message_id, direction, message_text, message_type, timestamp
- **Enums**:
  - MessageDirection (in, out)
  - MessageType (text, voice, image, document, video, audio, sticker, location, contact)
- **Computed Properties**: is_incoming, is_outgoing, is_voice, is_media, age_minutes

### 4. Proposal Model (`src/oneai_reach/domain/models/proposal.py`)
- **Fields**: id, lead_id, content, score, reviewed, reviewed_at, review_notes, created_at, updated_at
- **Validation**: score must be 0.0-10.0, rounded to 2 decimals
- **Computed Properties**: is_high_quality (≥7.0), is_reviewed, needs_revision (<5.0), word_count, char_count

### 5. KnowledgeEntry Model (`src/oneai_reach/domain/models/knowledge.py`)
- **Fields**: id, wa_number_id, category, question, answer, content, tags, priority, created_at, updated_at
- **Enum**: KnowledgeCategory (faq, doc, snippet)
- **Validation**: 
  - Priority 0-10
  - Tags normalized to lowercase
- **Computed Properties**: is_faq, is_snippet, is_high_priority (≥7), tag_list, searchable_text

## Validation Tests Results

### Email Validation ✓
- Invalid email "not-an-email" correctly rejected
- ValidationError: "value is not a valid email address: An email address must have an @-sign."

### Phone Normalization ✓
- 081234567890 → +6281234567890
- +6281234567890 → +6281234567890 (already normalized)
- 6281234567890 → +6281234567890

### Score Validation ✓
- Score > 10 rejected: "Input should be less than or equal to 10"
- Score < 0 rejected: "Input should be greater than or equal to 0"
- Valid score 8.5 accepted and rounded to 2 decimals

### Priority Validation ✓
- Priority > 10 rejected: "Input should be less than or equal to 10"
- Valid priority 0-10 accepted

### Tags Normalization ✓
- "PRICING, FAQ, General" → "pricing,faq,general"
- tag_list property returns: ['pricing', 'faq', 'general']

## Computed Properties Working ✓
- Lead.is_warm: True for REPLIED/MEETING_BOOKED status
- Lead.days_since_contact: Calculates days from contacted_at
- Lead.needs_followup: True after 3 days without reply
- Conversation.is_stale: True after 48 hours inactive
- Message.is_media: True for voice/image/video/document
- Proposal.is_high_quality: True for score ≥ 7.0
- KnowledgeEntry.is_high_priority: True for priority ≥ 7

## Key Implementation Details
- All models use `model_config = {"from_attributes": True}` for SQLAlchemy/sqlite3.Row compatibility
- Field validators use `@field_validator` decorator
- Computed properties use `@property` decorator
- Enums inherit from `str, Enum` for JSON serialization
- Optional fields use `Optional[Type] = None`
- DateTime fields use `datetime` type for automatic parsing

## Files Created
- `src/oneai_reach/domain/models/lead.py` (147 lines)
- `src/oneai_reach/domain/models/conversation.py` (79 lines)
- `src/oneai_reach/domain/models/message.py` (75 lines)
- `src/oneai_reach/domain/models/proposal.py` (66 lines)
- `src/oneai_reach/domain/models/knowledge.py` (87 lines)
- `src/oneai_reach/domain/models/__init__.py` (23 lines)

## Evidence Files
- `.sisyphus/evidence/task-3-lead-validation.txt` - Lead validation tests
- `.sisyphus/evidence/task-3-email-validation-error.txt` - Email validation error

## Database Compatibility
All models map directly to existing database schemas:
- Lead → leads table (state_manager.py)
- Conversation → conversations table (state_manager.py)
- Message → conversation_messages table (state_manager.py)
- Proposal → proposals table (to be created)
- KnowledgeEntry → knowledge_base table (state_manager.py)

## Next Steps
- Task 4: Repository pattern implementation
- Task 5: Application service layer
- Task 6: Migrate existing scripts to use domain models

## Task 4: Abstract Repository Interfaces

**Date:** 2026-04-17

### What We Built
Created three abstract repository interfaces using Python ABC for data access abstraction:
- `LeadRepository` (14 methods) - Lead persistence contract
- `ConversationRepository` (13 methods) - Conversation persistence contract
- `KnowledgeRepository` (15 methods) - Knowledge base persistence contract

### Key Patterns
1. **ABC + @abstractmethod** - All methods marked abstract, cannot be instantiated
2. **Type hints throughout** - Return types use domain models (Lead, Conversation, KnowledgeEntry)
3. **Comprehensive docstrings** - Each method documents Args, Returns, Raises
4. **Query methods** - Beyond CRUD: find_by_status, find_warm_leads, search, count_by_status, etc.
5. **WA-number scoping** - ConversationRepository and KnowledgeRepository methods scoped to wa_number_id

### Data Access Patterns Observed
From reference files (leads.py, conversation_tracker.py, kb_manager.py):
- **Leads**: CSV + SQLite hybrid (state_manager backend)
- **Conversations**: SQLite with state machine (active/resolved/escalated/cold)
- **Knowledge**: SQLite with FTS5 full-text search + outcome weighting

### Repository Method Categories
1. **CRUD**: get_by_id, get_all, save, update, delete
2. **Finders**: find_by_status, find_by_email, find_by_phone, find_by_website
3. **Queries**: find_warm_leads, find_cold_leads, find_needs_followup, find_stale
4. **Search**: search, search_with_outcome_weighting
5. **Aggregation**: count_by_status, count_by_category, count_total
6. **Bulk ops**: import_entries, export_entries

### Testing Verified
✓ Abstract classes cannot be instantiated (TypeError raised)
✓ All @abstractmethod decorators working
✓ ABC inheritance correct
✓ Type hints complete and valid
✓ Docstrings comprehensive

### Next Steps
- Implement concrete repositories (CSV, SQLite backends)
- Add repository factory/dependency injection
- Integrate with existing scripts (leads.py, conversation_tracker.py, kb_manager.py)

## Task 5: Structured Logging Infrastructure

**Date:** 2026-04-17

### What We Built
Created comprehensive structured logging infrastructure with JSON formatter and correlation ID support:
- `src/oneai_reach/infrastructure/logging/logger.py` (131 lines)
- JSONFormatter class for structured JSON output
- ColoredFormatter class for human-readable console output
- Correlation ID support via contextvars (thread-local storage)
- Log rotation configuration (10MB per file, keep 10 backups)
- `get_logger(name)` singleton with @lru_cache caching
- Context manager for correlation ID injection

### Key Components

#### 1. JSONFormatter
- Outputs logs as valid JSON with fields: timestamp, level, logger, message, correlation_id
- Includes exception traceback when present
- Supports extra fields via record.extra_fields
- ISO 8601 UTC timestamps

#### 2. ColoredFormatter
- Console output with ANSI color codes (DEBUG=cyan, INFO=green, WARNING=yellow, ERROR=red, CRITICAL=magenta)
- Displays correlation ID in brackets when present
- Human-readable format for development

#### 3. Correlation ID System
- Uses `contextvars.ContextVar` for thread-safe, async-safe storage
- Context manager: `with correlation_id_context('req-123'): ...`
- Direct access: `get_correlation_id()`, `set_correlation_id(id)`
- Automatically included in all logs within context
- Resets to None after context exit

#### 4. Logger Configuration
- Dual output: console (colored) + file (JSON)
- File handler uses RotatingFileHandler (10MB, 10 backups)
- Log files in `logs/` directory with pattern: `{logger_name}.log`
- Prevents propagation to root logger (isolated per logger)
- @lru_cache(maxsize=128) on get_logger() for performance

### Testing Results

#### Test 1: Basic Logger Creation ✓
- Console output shows colored, formatted messages
- File output creates JSON logs

#### Test 2: Correlation ID Context Manager ✓
- Correlation ID properly set within context
- Resets to None after context exit
- Displayed in console output in brackets

#### Test 3: Direct Correlation ID Setting ✓
- set_correlation_id() works correctly
- Persists across multiple log calls

#### Test 4: JSON Log File Verification ✓
- Log files created in logs/ directory
- All entries are valid JSON
- Schema: {timestamp, level, logger, message, correlation_id, exception?}

#### Test 5: Exception Logging ✓
- Exceptions logged with full traceback
- Exception field included in JSON output

### Sample JSON Log Entry
```json
{
  "timestamp": "2026-04-17T14:38:32.429251Z",
  "level": "INFO",
  "logger": "test.module",
  "message": "Test info message",
  "correlation_id": null
}
```

### Correlation ID Propagation Test
All three log calls within the same context received the same correlation ID:
- Processing order [order-req-2026-04-17-001]
- Validating payment [order-req-2026-04-17-001]
- Sending confirmation [order-req-2026-04-17-001]

### Integration Points
- Import: `from oneai_reach.infrastructure.logging.logger import get_logger, correlation_id_context`
- Usage: `logger = get_logger(__name__)`
- Request tracing: `with correlation_id_context(request_id): ...`

### Files Created
- `src/oneai_reach/infrastructure/logging/logger.py` (131 lines)
- `.sisyphus/evidence/task-5-json-log.txt` - JSON format verification
- `.sisyphus/evidence/task-5-correlation-id.txt` - Correlation ID test results

### Key Design Decisions
1. **contextvars over threading.local** - Better for async code, modern Python standard
2. **@lru_cache on get_logger** - Prevents duplicate handler registration
3. **Dual formatters** - JSON for machine parsing, colored for human debugging
4. **RotatingFileHandler** - Prevents log files from growing unbounded
5. **No propagation** - Each logger is isolated, prevents duplicate logs

### Next Steps
- Task 6: Integrate logging into existing scripts
- Task 7: Add structured logging to business logic
- Task 8: Create log aggregation/analysis tools

## Task 6: Custom Exception Hierarchy with Error Codes

**Date:** 2026-04-17

### What We Built
Created comprehensive exception hierarchy with 20 exception classes organized into 3 categories:
- `src/oneai_reach/domain/exceptions.py` (750+ lines)
- Base class: `OneAIReachException` with error_code and to_dict()
- 7 domain exceptions (LEAD_*, CONV_*, KB_*)
- 8 infrastructure exceptions (DB_*, API_*, CONFIG_*)
- 5 application exceptions (VAL_*, AUTH_*, RATE_*)

### Exception Categories

#### 1. Domain Exceptions (Business Logic)
- `LeadNotFoundError` (LEAD_001) - Lead not found by ID
- `InvalidLeadStatusError` (LEAD_002) - Invalid status transition
- `DuplicateLeadError` (LEAD_003) - Duplicate lead by email
- `ConversationNotFoundError` (CONV_001) - Conversation not found
- `InvalidConversationStateError` (CONV_002) - Invalid conversation state
- `KnowledgeNotFoundError` (KB_001) - Knowledge entry not found
- `InvalidKnowledgeError` (KB_002) - Knowledge constraint violation

#### 2. Infrastructure Exceptions (External Systems)
- `DatabaseError` (DB_001) - Database operation failed
- `DatabaseConnectionError` (DB_002) - Database connection failed
- `DatabaseIntegrityError` (DB_003) - Database constraint violation
- `ExternalAPIError` (API_001) - External API call failed
- `APITimeoutError` (API_002) - API call timed out
- `APIRateLimitError` (API_003) - API rate limit exceeded
- `ConfigurationError` (CONFIG_001) - Invalid configuration
- `MissingConfigurationError` (CONFIG_002) - Missing required config

#### 3. Application Exceptions (API/Validation)
- `ValidationError` (VAL_001) - Input validation failed
- `InvalidInputError` (VAL_002) - Input malformed
- `AuthenticationError` (AUTH_001) - Authentication failed
- `AuthorizationError` (AUTH_002) - User lacks permission
- `RateLimitError` (RATE_001) - Application rate limit exceeded

### Base Exception Class Design

```python
class OneAIReachException(Exception):
    def __init__(self, message: str, error_code: str, **kwargs):
        self.message = message
        self.error_code = error_code
        self.context = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_code': self.error_code,
            'message': self.message,
            'type': self.__class__.__name__,
            'context': self.context if self.context else None
        }
```

### Key Features

1. **Error Codes** - Programmatic identifiers for client-side handling
   - Format: `{CATEGORY}_{NUMBER}` (e.g., LEAD_001, API_002)
   - Enables error-specific UI/retry logic

2. **Context Preservation** - All relevant data captured in kwargs
   - Example: LeadNotFoundError captures lead_id
   - Example: ExternalAPIError captures service, endpoint, status_code
   - Enables debugging without re-raising

3. **JSON Serialization** - to_dict() method for API responses
   - Returns dict with error_code, message, type, context
   - Fully JSON serializable (tested with json.dumps/loads)
   - Enables REST API error responses

4. **Hierarchical Catching** - Can catch by category or specific type
   - `except DomainException:` catches all business logic errors
   - `except LeadNotFoundError:` catches specific error
   - `except OneAIReachException:` catches all system errors

5. **Comprehensive Docstrings** - Each exception documents:
   - When to raise it
   - Error code
   - Usage example
   - Constructor parameters

### Testing Results

#### Test 1: Exception Raising & Catching ✓
- All 20 exception types tested
- Raise/catch pattern verified
- Error codes correctly assigned
- Messages properly formatted

#### Test 2: to_dict() Method ✓
- Simple exceptions: error_code, message, type, context preserved
- Multi-field context: all fields captured correctly
- Numeric fields: port numbers, status codes preserved as integers
- Optional fields: None values handled correctly
- JSON serialization: to_dict() output fully JSON serializable

#### Test 3: Context Preservation ✓
- LeadNotFoundError: lead_id captured
- InvalidLeadStatusError: current_status, attempted_status, reason captured
- DatabaseConnectionError: host, port, reason captured
- ExternalAPIError: service, endpoint, status_code, reason captured
- RateLimitError: user_id, limit, window_seconds, retry_after_seconds captured

#### Test 4: Hierarchical Catching ✓
- Can catch by base class: `except OneAIReachException`
- Can catch by category: `except DomainException`, `except InfrastructureException`
- Can catch by specific type: `except LeadNotFoundError`

### Sample Usage

```python
# Raising
try:
    lead = repository.get_by_id("lead_123")
    if not lead:
        raise LeadNotFoundError(lead_id="lead_123")
except LeadNotFoundError as e:
    logger.error(f"Lead lookup failed: {e}")
    return {"error": e.to_dict()}, 404

# API Response
except ExternalAPIError as e:
    return {"error": e.to_dict()}, 502

# Retry Logic
except APIRateLimitError as e:
    retry_after = e.retry_after_seconds or 60
    time.sleep(retry_after)
    # retry...
```

### Files Created
- `src/oneai_reach/domain/exceptions.py` (750+ lines)
- `.sisyphus/evidence/task-6-exception-raise.txt` - All 20 exceptions tested
- `.sisyphus/evidence/task-6-exception-dict.txt` - to_dict() method tests

### Integration Points
- Import: `from oneai_reach.domain.exceptions import LeadNotFoundError, DatabaseError, ValidationError`
- Usage: Raise in repositories, services, and API handlers
- API responses: Use `exception.to_dict()` for error payloads

### Design Decisions
1. **Separate categories** - Domain/Infrastructure/Application for clear responsibility
2. **Error codes** - Programmatic identifiers enable client-side error handling
3. **Context kwargs** - Flexible context capture without subclass explosion
4. **to_dict() method** - JSON serialization for REST APIs
5. **Comprehensive docstrings** - Public API documentation with examples

### Next Steps
- Task 7: Integrate exceptions into repositories
- Task 8: Add exception handling to services
- Task 9: Create API error response middleware

## Wave 2 - Task 7 Part 1: Outreach Services Migration (2026-04-17)

### Services Created
- `ScraperService`: Multi-source lead scraping (Google Places, Yellow Pages, DuckDuckGo)
- `EnricherService`: Multi-strategy contact enrichment (AgentCash Minerva, website scraping, email patterns)
- `ResearcherService`: Prospect pain-point research and tech stack detection

### Patterns Applied
- Dependency injection: Services receive Settings via constructor
- Domain exceptions: Used ExternalAPIError, MissingConfigurationError with proper error codes
- Structured logging: Used get_logger(__name__) with correlation ID support
- Configuration: Used get_settings() from Pydantic Settings
- Backward compatibility: Original scripts remain as thin CLI wrappers

### Key Design Decisions
- Services return dict instead of domain models for now (Lead model conversion deferred to Task 12)
- Services are synchronous (async refactoring deferred to Wave 3)
- External API clients (AgentCash subprocess, requests) kept as-is (will be abstracted in Task 13)
- Original scripts updated to instantiate services and delegate business logic
- All business logic extracted from scripts into testable service methods

### Verification Results
- All 3 service classes import successfully
- Original scripts execute without errors
- Business logic preserved (scraper finds leads, enricher enriches, researcher researches)
- Backward compatibility maintained (scripts still work as CLI tools)


## Task 9: Voice Pipeline Services Migration (2026-04-17)

### Services Created
- `stt_service.py`: STT with faster-whisper, lazy-loading, singleton pattern
- `tts_service.py`: TTS with ChatterBox, CPU fallback for OOM
- `audio_service.py`: Audio conversion (WAV/OGG) via ffmpeg subprocess
- `voice_pipeline_service.py`: End-to-end orchestration (download → STT → LLM → TTS → send)

### Key Patterns Applied
- **Dependency Injection**: All services receive `Settings` in constructor
- **Lazy Loading**: ML models loaded on first use to avoid startup overhead
- **Error Handling**: Custom exceptions (`ExternalAPIError`, `MissingConfigurationError`)
- **Logging**: Structured logging via `get_logger(__name__)`
- **Singleton Helpers**: `get_stt_service()`, `get_tts_service()` for backward compatibility

### Backward Compatibility
- Original scripts (`stt_engine.py`, `tts_engine.py`, `audio_utils.py`, `voice_pipeline.py`) converted to thin wrappers
- All existing function signatures preserved
- Scripts delegate to new services via `sys.path` injection
- Zero breaking changes for existing callers

### Voice-Specific Considerations
- **STT**: faster-whisper requires file paths (temp files used)
- **TTS**: ChatterBox has automatic CPU fallback for GPU OOM
- **Audio**: ffmpeg subprocess for lightweight conversion (no heavy ML libs)
- **Pipeline**: Integrates with existing `cs_engine` and `senders` modules

### Configuration
- Voice settings loaded from environment variables (VOICE_STT_*, VOICE_TTS_*)
- Per-session config via `state_manager.get_voice_config(session_name)`
- Fallback to env defaults if DB lookup fails

### Import Verification
```bash
python -c "from oneai_reach.application.voice import STTService, TTSService, AudioService, VoicePipelineService"
# ✓ All 4 services import OK
```


### Wave 2 Progress Summary
- **Task 7**: ✓ 10 outreach services migrated
- **Task 8**: ✓ 7 CS engine services migrated
- **Task 9**: ✓ 4 voice pipeline services migrated (THIS TASK)

**Total Services Created in Wave 2**: 21 services across 3 application domains


## Task 11: Domain Services Created (2026-04-17)

Created 4 pure business logic domain services with NO external dependencies:

### Services Created
1. **LeadScoringService** (`lead_scoring_service.py`)
   - Calculates lead quality scores (0-100 scale)
   - Algorithm: Base 20 + contact info (30) + web presence (20) + research (10) + engagement (30) - negative signals (50)
   - Categories: hot (70+), warm (50-69), cold (30-49), dead (0-29)
   - Method: `calculate_score(lead: Lead) → int`

2. **ConversationAnalyzer** (`conversation_analyzer.py`)
   - Sentiment analysis: positive/neutral/negative (keyword-based)
   - Intent detection: question/complaint/purchase/feedback/other
   - Engagement level: high/medium/low
   - Method: `analyze(text: str) → dict`
   - Supports batch analysis and aggregate sentiment

3. **ProposalValidator** (`proposal_validator.py`)
   - Pass threshold: 6/10 (from reviewer.py PASS_THRESHOLD)
   - High quality threshold: 7/10
   - Word count validation: 50-500 words
   - Method: `is_passing(score: int) → bool`
   - Revision priority levels: critical/high/medium/low/none

4. **FunnelCalculator** (`funnel_calculator.py`)
   - Calculates funnel metrics across 13 stages (from leads.py FUNNEL_STAGES)
   - Conversion rates: enrichment, review pass, contact, reply, meeting, close
   - Win/loss rates and active pipeline count
   - Method: `calculate_metrics(leads: List[Lead]) → dict`
   - Health scoring and bottleneck detection

### Key Patterns
- All services are stateless (pure functions or stateless classes)
- No external dependencies (no DB, no API, no logging, no Settings)
- Use domain models (Lead, Conversation, Proposal) for input/output
- Comprehensive docstrings explaining business rules
- All business logic extracted from scripts: reviewer.py, leads.py, cs_analytics.py, guard_checker.py

### Verification
- All services instantiate without errors ✅
- All methods callable and return correct types ✅
- Business logic preserved from original scripts ✅
- Test coverage: scoring, sentiment analysis, validation, funnel metrics ✅


## Task 10: Agent Orchestration Migration (2026-04-17)

### Services Completed
- **warmcall_service.py** (680 lines) - Multi-turn follow-up orchestration
- **autonomous_service.py** (103 lines) - Autonomous OODA loop
- Total: 4 agent services, 1,191 lines

### Key Patterns Applied
1. **Service extraction from large scripts**:
   - warmcall_engine.py (900 lines) → WarmcallService (680 lines)
   - autonomous_loop.py (177 lines) → AutonomousService (103 lines)
   - Reduced complexity while preserving all functionality

2. **Configuration via Settings**:
   - `config.warmcall.followup_intervals` - timing configuration
   - `config.warmcall.max_turns` - max follow-up attempts
   - `config.autonomous.loop_sleep_seconds` - OODA loop timing
   - `config.autonomous.min_new_leads_threshold` - scraping trigger

3. **Method naming conventions**:
   - Public methods: `start_warmcall()`, `process_due_warmcalls()`
   - Private helpers: `_days_since()`, `_outbound_turn_count()`
   - Consistent with established pattern

4. **Preserved business logic**:
   - Warmcall intervals: [1, 3, 7, 14] days exactly
   - Max turns: 4 (then mark cold)
   - Intent routing: BUY → converter, REJECT → cold, INFO/UNCLEAR → reply
   - Decision tree: 10 dispatch rules based on funnel state
   - All prompts and strategies unchanged

### Challenges Solved
1. **Large script migration**: warmcall_engine.py had 900 lines with complex state management
   - Solution: Extracted into cohesive service with clear method boundaries
   - Preserved all timing logic and intent classification

2. **Subprocess management**: autonomous_loop.py tracked running processes
   - Solution: Moved `_running` dict to instance variable
   - Maintained non-blocking dispatch pattern

3. **Method signature consistency**: Original used different parameter names
   - Solution: Standardized to `phone`, `name`, `session` (not `wa_number_id`, `contact_phone`, `contact_name`)
   - Maintains consistency with other services

### Verification Results
✅ All services compile without syntax errors
✅ All services instantiate with mock Settings
✅ All required methods present and callable
✅ Dependency injection pattern followed
✅ Logging via get_logger(__name__)
✅ ExternalAPIError for failures

### Next Steps
- Task 11: Domain services (lead scoring, conversation analysis)
- Update original scripts to call services (thin wrappers)
- Add unit tests for agent services


## Task 14: Messaging Infrastructure Migration (2026-04-17)

### Implementation Summary
Successfully migrated messaging infrastructure from `scripts/senders.py` to `src/oneai_reach/infrastructure/messaging/` with complete fallback chains and delivery tracking.

### Files Created
1. `email_sender.py` - Email sending with Brevo → Stalwart → gog → himalaya → queue fallback
2. `whatsapp_sender.py` - WhatsApp sending with WAHA → wacli fallback
3. `message_queue.py` - JSON-based queue for rate limiting and retry management
4. `__init__.py` - Package exports

### Key Design Decisions
- **Dependency Injection**: Settings injected via constructor (no global state)
- **Fallback Chains**: Preserved exact order from original implementation
- **Phone Format Handling**: Supports @lid (WAHA webhook) and @c.us formats
- **Queue Persistence**: JSON format for human-readable queue inspection
- **Error Handling**: Each fallback method catches exceptions independently
- **Rate Limiting**: Delegated to WAHAClient (already implemented in Task 13)

### Email Fallback Chain
1. Brevo HTTP API (300/day free, trusted IP)
2. Stalwart SMTP (marketing@berkahkarya.org)
3. gog CLI (Gmail via gog)
4. himalaya CLI (IMAP/SMTP)
5. Queue to file (last resort for manual review)

### WhatsApp Fallback Chain
1. WAHA HTTP API (tries both WAHA_URL and WAHA_DIRECT_URL)
2. wacli CLI (local WhatsApp client)

### Message Queue Features
- JSON-based persistence (logs/email_queue.log)
- Status tracking: pending, sent, failed
- Retry count tracking
- Statistics: total, pending, sent, failed counts
- Cleanup: remove sent messages to prevent log bloat

### Testing Results
✅ All classes import successfully
✅ EmailSender instantiates with correct queue path
✅ WhatsAppSender instantiates with default session
✅ MessageQueue creates log file and tracks messages
✅ Queue operations (add, get_stats) work correctly

### Integration Points
- Uses Settings from Task 2 (Pydantic Settings)
- Uses WAHAClient from Task 13 (External Clients)
- Uses domain exceptions from Task 6 (Custom Exceptions)
- Queue log path respects settings.database.logs_dir

## Task 16: Webhook Endpoints Migration (2026-04-17)

### Implementation Pattern
- Created FastAPI routers in `src/oneai_reach/api/webhooks/` following established patterns
- WAHA webhook: handles WhatsApp message/status events with duplicate detection, rate limiting, voice support
- CAPI webhook: handles Meta Conversions API lead tracking (lead/purchase/atc events)
- Used Pydantic models for request validation (automatic 422 on invalid payloads)
- Preserved exact webhook behavior from original Flask implementation

### Key Decisions
- Kept `webhook_server.py` as backward compatibility wrapper with deprecation notice
- Injected services via direct imports (cs_engine, state_manager, capi_tracker) - no DI needed for stateless functions
- Used global `_processed_messages` set for duplicate detection (same as original)
- Preserved all guards: duplicate detection, from_me filter, group message filter, manual mode check
- Voice pipeline integration preserved with try/except for optional voice_config module

### Testing Results
- ✓ CAPI router imports successfully
- ✓ WAHA router imports successfully
- ✓ FastAPI app creates with routers registered
- ✓ Valid CAPI payload returns 200 with tracked=true
- ✓ Invalid CAPI payload returns 422 with Pydantic validation errors
- ✓ WAHA webhook returns 404 for unknown session (expected behavior)
- ✓ WAHA webhook returns 200 for valid events
- ✓ All routes registered: /api/v1/webhooks/waha/message, /api/v1/webhooks/waha/status, /api/v1/webhooks/capi/lead

### Routes Registered
```
POST /api/v1/webhooks/waha/message  - WhatsApp message events
POST /api/v1/webhooks/waha/status   - WhatsApp status events
POST /api/v1/webhooks/capi/lead     - Meta CAPI lead tracking
```


### Migration Summary
Successfully migrated all webhook endpoints from Flask (webhook_server.py) to FastAPI:
- **WAHA webhooks**: Message and status events with full feature parity (duplicate detection, voice support, manual mode)
- **CAPI webhooks**: Meta Conversions API lead tracking (lead/purchase/atc)
- **Validation**: Pydantic models provide automatic 422 responses for invalid payloads
- **Backward compatibility**: webhook_server.py updated with deprecation notice pointing to new API
- **Testing**: All endpoints verified with curl (200/404/422 status codes working correctly)

Next: Task 17 will migrate remaining API endpoints (leads, conversations, KB, services).


## Task 17: MCP Server Migration (2026-04-18)

### Implementation Summary
- Migrated 34 MCP methods from `mcp_server.py` to `src/oneai_reach/api/v1/mcp.py`
- Implemented JSON-RPC 2.0 protocol compliance with proper error codes
- All handlers standardized with `params: Dict[str, Any] = None` signature
- Added `params = params or {}` guard in all handlers to prevent None access errors
- Invocation logic uses `handler(params or {})` for consistent parameter passing

### Key Patterns
1. **Handler Signature**: All handlers accept optional params dict with default None
2. **Null Safety**: `params = params or {}` at start of handlers that access params
3. **JSON-RPC Errors**: Standard error codes (-32700 parse, -32600 invalid request, -32601 method not found, -32602 invalid params, -32603 internal error)
4. **Method Registry**: Dictionary mapping method names to handler functions
5. **Discovery Endpoint**: GET /api/v1/mcp/methods returns all available methods

### Files Modified
- `src/oneai_reach/api/v1/mcp.py` (547 lines) - New MCP endpoints
- `src/oneai_reach/api/main.py` - Registered MCP router
- `mcp_server.py` - Updated with deprecation notice (backward compat wrapper)

### Verification Results
✓ All 34 MCP methods migrated and working
✓ JSON-RPC 2.0 protocol compliance maintained
✓ Request/response logging added
✓ Services injected via agent_control module
✓ Original MCP behavior preserved
✓ Import tests pass
✓ Curl tests return valid JSON-RPC responses
✓ Error handling works correctly

### Critical Bug Fixed
- Handler signature mismatch: Empty params dict `{}` was treated as falsy by `if params:`
- Solution: Changed to `handler(params or {})` and added null guards in all handlers
- All handlers now work with both empty and populated params


## Migration Guide Creation (Task 27)

**Date:** 2026-04-18

**What was done:**
- Enhanced existing migration guide from 543 lines to 1131 lines
- Added comprehensive command mapping for all CLI command groups (funnel, stages, jobs, wa, test, system, kb)
- Documented all environment variable prefix changes (DB_, SMTP_, GMAIL_, PIPELINE_, LLM_, CS_, etc.)
- Added detailed service restart instructions for systemd, shell scripts, Docker, and cron jobs
- Created troubleshooting section with 10+ common issues and solutions
- Expanded FAQ section with 20+ questions covering migration scenarios
- Added quick migration checklist for teams
- Documented deprecation schedule (Phase 1-3, April-October 2026)

**Key patterns:**
- New CLI uses command groups: `oneai-reach <group> <command>`
- Pipeline stages: `oneai-reach stages run <stage> --args "arg1" --args "arg2"`
- Background jobs: `oneai-reach stages start <stage>` + `oneai-reach jobs list/stop`
- All old scripts are shims that call new CLI with deprecation warnings
- Configuration now uses Pydantic Settings with prefixed env vars

**Migration complexity:**
- Environment variables: Optional during compatibility (old vars still work)
- Cron jobs: Simple find/replace of command paths
- Systemd services: Update ExecStart line + add WorkingDirectory
- Docker: Update CMD in Dockerfile
- Custom scripts: Update imports from `scripts.*` to `oneai_reach.*`

**Evidence:**
- File created: docs/migration_guide.md (27KB, 1131 lines)
- Evidence file: .sisyphus/evidence/task-27-migration-guide.txt
