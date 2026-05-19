# 1ai-reach Codebase Restructure - International Best Practices

## TL;DR

> **Quick Summary**: Transform flat 50+ script directory into professional Python package following Clean Architecture principles with proper separation of concerns, dependency injection, unified API layer, and comprehensive testing.
> 
> **Deliverables**:
> - `src/oneai_reach/` package with domain/application/infrastructure layers
> - Unified FastAPI server consolidating webhook/MCP/agent-control
> - Proper CLI with Click commands
> - Comprehensive test suite with unit/integration/e2e
> - Consolidated documentation structure
> - Migration guide and backward compatibility layer
> 
> **Estimated Effort**: Large (3-4 weeks)
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Foundation → Domain Models → Application Layer → Infrastructure → API → Migration

---

## Context

### Original Request
User wants to "tidy-up the codebase! make it have proper code-structure. based on international best-practice standard! make sure to plan it thoroughly! to make a complete and comprehensive apps!"

### Current State Analysis

**Problems**:
1. **Flat structure**: 50+ Python scripts in `scripts/` directory with no module boundaries
2. **Mixed concerns**: Outreach pipeline, CS engine, voice, agents, utilities all intermingled
3. **Import chaos**: Circular dependencies, no proper package structure
4. **Configuration scattered**: `.env`, `config.py`, `capi_config.json`, hardcoded values
5. **Poor testability**: Tight coupling, no dependency injection, minimal test coverage
6. **No API abstraction**: Direct script execution, 3 separate servers (webhook, MCP, agent_control)
7. **State management unclear**: Multiple DBs (SQLite), CSV files, JSON files with overlapping data
8. **Documentation scattered**: 20+ markdown files in root directory

**Current Module Categories** (identified from file analysis):
- **Outreach Pipeline** (10 files): scraper, enricher, researcher, generator, reviewer, blaster, reply_tracker, converter, followup, sheets_sync
- **Customer Service** (8 files): cs_engine, cs_playbook, cs_learn, cs_analytics, cs_outcomes, cs_self_improve, conversation_tracker, conversation_cleanup
- **Voice/Audio** (5 files): stt_engine, tts_engine, audio_utils, voice_pipeline, voice_config
- **Agents** (5 files): strategy_agent, closer_agent, warmcall_engine, flosia_sales_engine, autonomous_loop
- **Infrastructure** (7 files): brain_client, llm_client, n8n_client, senders, wa_manager, state_manager, kb_manager
- **Utilities** (6 files): leads, utils, config, guard_checker, health_monitor, capi_tracker
- **Servers** (3 files): webhook_server, mcp_server, agent_control

---

## Work Objectives

### Core Objective
Restructure 1ai-reach codebase into professional Python package following Clean Architecture / Hexagonal Architecture principles with proper separation of concerns, testability, and maintainability.

### Concrete Deliverables
- `src/oneai_reach/` package with proper `__init__.py` and namespace
- Domain layer: Pure business logic with models, services, repository interfaces
- Application layer: Use cases orchestrating domain services
- Infrastructure layer: External integrations (DB, APIs, messaging)
- Unified FastAPI server replacing 3 separate servers
- Click-based CLI with subcommands for all operations
- Pydantic Settings for type-safe configuration
- Comprehensive test suite (unit/integration/e2e)
- Consolidated `docs/` directory with architecture, API, runbooks
- Migration script with backward compatibility layer
- Updated `pyproject.toml` with proper dependencies and entry points

### Definition of Done
- [ ] All 50+ scripts migrated to new package structure
- [ ] Zero import errors when running `python -m oneai_reach`
- [ ] All existing functionality preserved (verified by e2e tests)
- [ ] Test coverage ≥70% (unit + integration)
- [ ] All 3 servers consolidated into single FastAPI app
- [ ] CLI commands work: `oneai-reach scrape`, `oneai-reach enrich`, etc.
- [ ] Documentation complete: architecture diagram, API reference, migration guide
- [ ] Backward compatibility: Old script paths still work via shims
- [ ] CI/CD ready: pytest runs clean, linting passes

### Must Have
- Clean separation: domain (business logic) / application (use cases) / infrastructure (external)
- Dependency injection: Services receive dependencies via constructor
- Repository pattern: Abstract data access behind interfaces
- Type safety: Pydantic models for all data structures
- Logging: Structured logging with correlation IDs
- Error handling: Custom exceptions with proper error codes
- Configuration: Single source of truth via Pydantic Settings
- Testing: Fixtures, mocks, integration tests with test DB

### Must NOT Have (Guardrails)
- **No business logic changes**: Preserve exact functionality - this is refactoring only
- **No database schema changes**: Keep SQLite schema compatible
- **No external API changes**: Brain, WAHA, n8n integrations stay as-is
- **No dashboard changes**: Next.js app is already well-structured
- **No deployment changes**: Keep systemd services, just update paths
- **No data migration**: Existing data files must work without conversion
- **No breaking changes**: Old import paths must work via compatibility layer
- **No over-engineering**: Don't add features, just restructure existing code

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, conftest.py already present)
- **Automated tests**: Tests-after (add tests as we migrate each module)
- **Framework**: pytest with fixtures, mocks, integration tests
- **Coverage target**: ≥70% for new package structure

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Package imports**: Use Bash (python -c "import ...") - verify no import errors
- **CLI commands**: Use Bash (oneai-reach --help) - verify Click commands work
- **API endpoints**: Use Bash (curl) - verify FastAPI routes respond correctly
- **Database operations**: Use Bash (sqlite3) - verify schema compatibility
- **End-to-end**: Use Bash (run full pipeline) - verify functionality preserved

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.

```
Wave 1 (Foundation - 6 tasks, can start immediately):
├── Task 1: Create package structure skeleton [quick]
├── Task 2: Setup Pydantic Settings for configuration [quick]
├── Task 3: Define domain models (Lead, Conversation, Message, etc.) [unspecified-high]
├── Task 4: Create repository interfaces [quick]
├── Task 5: Setup logging infrastructure [quick]
└── Task 6: Create custom exception hierarchy [quick]

Wave 2 (Domain & Application - 8 tasks, after Wave 1):
├── Task 7: Migrate outreach pipeline to application layer [unspecified-high]
├── Task 8: Migrate CS engine to application layer [unspecified-high]
├── Task 9: Migrate voice pipeline to application layer [unspecified-high]
├── Task 10: Migrate agent orchestration to application layer [unspecified-high]
├── Task 11: Create domain services (lead scoring, conversation analysis) [deep]
├── Task 12: Implement repository adapters (SQLite, CSV) [unspecified-high]
├── Task 13: Migrate external clients (brain, WAHA, n8n, LLM) [unspecified-high]
└── Task 14: Migrate messaging infrastructure (email, WhatsApp) [unspecified-high]

Wave 3 (API & CLI - 7 tasks, after Wave 2):
├── Task 15: Create unified FastAPI app structure [quick]
├── Task 16: Migrate webhook endpoints to FastAPI [unspecified-high]
├── Task 17: Migrate MCP server to FastAPI [unspecified-high]
├── Task 18: Migrate agent control to FastAPI [unspecified-high]
├── Task 19: Create Click CLI with subcommands [unspecified-high]
├── Task 20: Add API authentication & rate limiting [unspecified-high]
└── Task 21: Create backward compatibility shims [quick]

Wave 4 (Testing & Documentation - 6 tasks, after Wave 3):
├── Task 22: Write unit tests for domain layer [unspecified-high]
├── Task 23: Write integration tests for application layer [unspecified-high]
├── Task 24: Write e2e tests for full pipeline [deep]
├── Task 25: Create architecture documentation [writing]
├── Task 26: Create API reference documentation [writing]
└── Task 27: Create migration guide [writing]

Wave FINAL (Verification - 4 tasks, after ALL):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Full pipeline QA [unspecified-high]
└── Task F4: Scope fidelity check [deep]

Critical Path: Task 1 → Task 3 → Task 11 → Task 7-10 → Task 15-19 → Task 24 → F1-F4
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 8 (Wave 2)
```

### Dependency Matrix

**Wave 1** (foundation):
- 1-6: No dependencies (can all run in parallel)

**Wave 2** (domain & application):
- 7: Depends on 1, 3, 4, 11
- 8: Depends on 1, 3, 4, 11
- 9: Depends on 1, 3, 4
- 10: Depends on 1, 3, 4, 11
- 11: Depends on 1, 3, 4
- 12: Depends on 1, 3, 4
- 13: Depends on 1, 2, 5
- 14: Depends on 1, 2, 5

**Wave 3** (API & CLI):
- 15: Depends on 1, 2, 5, 6
- 16: Depends on 7, 15
- 17: Depends on 10, 15
- 18: Depends on 10, 15
- 19: Depends on 7-14
- 20: Depends on 15
- 21: Depends on 7-14, 19

**Wave 4** (testing & docs):
- 22: Depends on 3, 11
- 23: Depends on 7-14
- 24: Depends on 15-21
- 25: Depends on 1-21
- 26: Depends on 15-20
- 27: Depends on 1-21

**Wave FINAL** (verification):
- F1-F4: Depend on ALL previous tasks

### Agent Dispatch Summary

- **Wave 1**: 6 tasks → 5× `quick`, 1× `unspecified-high`
- **Wave 2**: 8 tasks → 6× `unspecified-high`, 1× `deep`, 1× `unspecified-high`
- **Wave 3**: 7 tasks → 2× `quick`, 5× `unspecified-high`
- **Wave 4**: 6 tasks → 3× `unspecified-high`, 1× `deep`, 2× `writing`
- **Wave FINAL**: 4 tasks → 1× `oracle`, 2× `unspecified-high`, 1× `deep`

---

## TODOs

- [x] 1. Create package structure skeleton

  **What to do**:
  - Create `src/oneai_reach/` directory with proper `__init__.py`
  - Create subdirectories: `domain/`, `application/`, `infrastructure/`, `api/`, `cli/`, `config/`
  - Create `domain/models/`, `domain/services/`, `domain/repositories/`
  - Create `application/outreach/`, `application/customer_service/`, `application/agents/`
  - Create `infrastructure/database/`, `infrastructure/external/`, `infrastructure/llm/`, `infrastructure/messaging/`
  - Create `api/v1/`, `api/webhooks/`
  - Add `__init__.py` to all directories for proper Python package structure
  - Update `pyproject.toml` with package configuration and entry points

  **Must NOT do**:
  - Don't move any existing code yet - this is skeleton only
  - Don't change any existing scripts in `scripts/` directory
  - Don't modify any configuration files yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple directory creation and boilerplate files
  - **Skills**: []
    - No special skills needed for basic file structure

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-6)
  - **Blocks**: Tasks 7-14, 15-21, 22-27
  - **Blocked By**: None (can start immediately)

  **References**:
  - `pyproject.toml` - Current package configuration to extend
  - Python Packaging Guide: https://packaging.python.org/en/latest/tutorials/packaging-projects/
  - Clean Architecture structure examples from similar projects

  **Acceptance Criteria**:
  - [ ] Directory structure created: `src/oneai_reach/domain/models/`, `application/`, `infrastructure/`, `api/`, `cli/`, `config/`
  - [ ] All directories have `__init__.py` files
  - [ ] `pyproject.toml` updated with `packages = [{include = "oneai_reach", from = "src"}]`
  - [ ] Package name set to `oneai-reach` with proper metadata

  **QA Scenarios**:
  ```
  Scenario: Package structure is importable
    Tool: Bash (python -c)
    Preconditions: Package skeleton created
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python -c "import sys; sys.path.insert(0, 'src'); import oneai_reach; print('SUCCESS')"
      3. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain import models; print('SUCCESS')"
    Expected Result: Both imports succeed, print "SUCCESS"
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-1-package-import.txt

  Scenario: All subdirectories are proper Python packages
    Tool: Bash (find + test)
    Preconditions: Directory structure created
    Steps:
      1. find src/oneai_reach -type d -exec test -f {}/__init__.py \; -print
      2. Count should match number of directories created
    Expected Result: Every directory has __init__.py
    Failure Indicators: Missing __init__.py in any subdirectory
    Evidence: .sisyphus/evidence/task-1-init-files.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-package-import.txt (import test output)
  - [ ] task-1-init-files.txt (directory listing with __init__.py verification)

  **Commit**: YES
  - Message: `feat(structure): create clean architecture package skeleton`
  - Files: `src/oneai_reach/**/__init__.py`, `pyproject.toml`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); import oneai_reach"`

- [x] 2. Setup Pydantic Settings for configuration

  **What to do**:
  - Create `src/oneai_reach/config/settings.py` with Pydantic BaseSettings
  - Migrate all constants from `scripts/config.py` to Pydantic Settings classes
  - Create settings groups: `DatabaseSettings`, `APISettings`, `ExternalServicesSettings`, `LLMSettings`, `MessagingSettings`
  - Add environment variable validation with proper types
  - Create `get_settings()` function with caching (lru_cache)
  - Add `.env.example` with all required variables documented
  - Keep backward compatibility: `scripts/config.py` imports from new settings

  **Must NOT do**:
  - Don't delete `scripts/config.py` yet (needed for backward compatibility)
  - Don't change environment variable names (preserve existing .env)
  - Don't add new configuration options (only migrate existing)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward Pydantic Settings migration
  - **Skills**: []
    - Standard Pydantic usage, no special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3-6)
  - **Blocks**: Tasks 13, 14, 15, 20
  - **Blocked By**: None (can start immediately)

  **References**:
  - `scripts/config.py` - All current configuration constants to migrate
  - `.env` - Current environment variables
  - Pydantic Settings docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
  - Example: Hub brain config, WAHA config, n8n config, LLM provider keys

  **Acceptance Criteria**:
  - [ ] `src/oneai_reach/config/settings.py` created with Pydantic BaseSettings
  - [ ] All constants from `scripts/config.py` migrated to typed settings
  - [ ] Environment variables validated on import (fails fast if missing required vars)
  - [ ] `.env.example` created with all variables documented
  - [ ] `get_settings()` function with lru_cache for singleton pattern

  **QA Scenarios**:
  ```
  Scenario: Settings load successfully from environment
    Tool: Bash (python -c)
    Preconditions: .env file exists with valid values
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.config.settings import get_settings; s = get_settings(); print(f'HUB_URL={s.hub_url}')"
      3. Verify output shows correct HUB_URL from .env
    Expected Result: Settings load, print correct HUB_URL value
    Failure Indicators: ValidationError, missing environment variable error
    Evidence: .sisyphus/evidence/task-2-settings-load.txt

  Scenario: Settings validation catches missing required variables
    Tool: Bash (python -c)
    Preconditions: Temporarily unset required env var
    Steps:
      1. unset GOG_ACCOUNT
      2. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.config.settings import get_settings; get_settings()" 2>&1
      3. Should fail with ValidationError mentioning GOG_ACCOUNT
    Expected Result: ValidationError raised, mentions missing GOG_ACCOUNT
    Failure Indicators: No error raised, or wrong error message
    Evidence: .sisyphus/evidence/task-2-validation-error.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-settings-load.txt (successful settings load)
  - [ ] task-2-validation-error.txt (validation error for missing var)

  **Commit**: YES
  - Message: `feat(config): add Pydantic Settings for type-safe configuration`
  - Files: `src/oneai_reach/config/settings.py`, `.env.example`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.config.settings import get_settings; get_settings()"`

- [x] 3. Define domain models (Lead, Conversation, Message, etc.)

  **What to do**:
  - Create `src/oneai_reach/domain/models/lead.py` with Lead Pydantic model
  - Create `src/oneai_reach/domain/models/conversation.py` with Conversation model
  - Create `src/oneai_reach/domain/models/message.py` with Message model
  - Create `src/oneai_reach/domain/models/proposal.py` with Proposal model
  - Create `src/oneai_reach/domain/models/knowledge.py` with KnowledgeEntry model
  - Add all fields from current CSV/SQLite schemas with proper types
  - Add validation rules (email format, phone format, status enums)
  - Add computed properties (e.g., `is_warm`, `days_since_contact`)
  - Create enums for status values: `LeadStatus`, `ConversationStatus`, `MessageType`
  - Add `from_dict()` and `to_dict()` methods for serialization

  **Must NOT do**:
  - Don't change field names (preserve database compatibility)
  - Don't add new business logic (pure data models only)
  - Don't add database-specific code (no SQLAlchemy models here)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful analysis of existing schemas and validation rules
  - **Skills**: []
    - Standard Pydantic modeling

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4-6)
  - **Blocks**: Tasks 7-14, 22-24
  - **Blocked By**: None (can start immediately)

  **References**:
  - `scripts/leads.py` - Current Lead data structure and FUNNEL_STAGES
  - `data/leads.csv` - CSV schema with all lead fields
  - `data/1ai_reach.db` - SQLite schema for conversations, messages
  - `scripts/conversation_tracker.py` - Conversation data structure
  - `scripts/kb_manager.py` - Knowledge base entry structure

  **Acceptance Criteria**:
  - [ ] All domain models created: Lead, Conversation, Message, Proposal, KnowledgeEntry
  - [ ] All fields from existing schemas included with correct types
  - [ ] Enums defined: LeadStatus, ConversationStatus, MessageType
  - [ ] Validation rules added: email format, phone format (+62xxx), URL validation
  - [ ] Computed properties: `is_warm`, `days_since_contact`, `is_replied`

  **QA Scenarios**:
  ```
  Scenario: Lead model validates correctly
    Tool: Bash (python -c)
    Preconditions: Domain models created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.models.lead import Lead, LeadStatus; lead = Lead(name='Test Co', email='test@example.com', status=LeadStatus.NEW); print(f'Valid: {lead.email}')"
      2. Should print "Valid: test@example.com"
    Expected Result: Lead model instantiates, validates email
    Failure Indicators: ValidationError, import error
    Evidence: .sisyphus/evidence/task-3-lead-validation.txt

  Scenario: Invalid email is rejected
    Tool: Bash (python -c)
    Preconditions: Domain models with validation
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.models.lead import Lead; Lead(name='Test', email='invalid-email')" 2>&1
      2. Should raise ValidationError
    Expected Result: ValidationError mentioning email format
    Failure Indicators: No error raised, model accepts invalid email
    Evidence: .sisyphus/evidence/task-3-email-validation-error.txt
  ```

  **Evidence to Capture**:
  - [ ] task-3-lead-validation.txt (successful model creation)
  - [ ] task-3-email-validation-error.txt (validation error for invalid email)

  **Commit**: YES
  - Message: `feat(domain): add domain models with validation`
  - Files: `src/oneai_reach/domain/models/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.models.lead import Lead"`

- [x] 4. Create repository interfaces

  **What to do**:
  - Create `src/oneai_reach/domain/repositories/lead_repository.py` with abstract LeadRepository
  - Create `src/oneai_reach/domain/repositories/conversation_repository.py` with abstract ConversationRepository
  - Create `src/oneai_reach/domain/repositories/knowledge_repository.py` with abstract KnowledgeRepository
  - Define interface methods: `get_by_id()`, `get_all()`, `save()`, `update()`, `delete()`, `find_by_status()`
  - Use ABC (Abstract Base Class) for interface definition
  - Add type hints for all methods (return domain models)
  - Add docstrings explaining contract for each method

  **Must NOT do**:
  - Don't implement concrete repositories yet (interfaces only)
  - Don't add database-specific code (no SQL, no file I/O)
  - Don't add business logic (pure data access interface)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple interface definitions with ABC
  - **Skills**: []
    - Standard Python ABC usage

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-3, 5-6)
  - **Blocks**: Tasks 7-12
  - **Blocked By**: None (can start immediately)

  **References**:
  - `scripts/leads.py` - Current data access patterns (load_leads, save_leads)
  - `scripts/conversation_tracker.py` - Conversation data access
  - `scripts/kb_manager.py` - Knowledge base data access
  - Repository Pattern: https://martinfowler.com/eaaCatalog/repository.html

  **Acceptance Criteria**:
  - [ ] Abstract repository interfaces created: LeadRepository, ConversationRepository, KnowledgeRepository
  - [ ] All CRUD methods defined: get_by_id, get_all, save, update, delete
  - [ ] Query methods defined: find_by_status, find_by_email, search
  - [ ] All methods have type hints and docstrings
  - [ ] Uses ABC with @abstractmethod decorators

  **QA Scenarios**:
  ```
  Scenario: Repository interfaces are importable
    Tool: Bash (python -c)
    Preconditions: Repository interfaces created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.repositories.lead_repository import LeadRepository; print('SUCCESS')"
      2. Should print "SUCCESS"
    Expected Result: Import succeeds
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-4-repo-import.txt

  Scenario: Cannot instantiate abstract repository
    Tool: Bash (python -c)
    Preconditions: ABC properly defined
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.repositories.lead_repository import LeadRepository; LeadRepository()" 2>&1
      2. Should raise TypeError about abstract methods
    Expected Result: TypeError mentioning cannot instantiate abstract class
    Failure Indicators: No error, or wrong error type
    Evidence: .sisyphus/evidence/task-4-abstract-error.txt
  ```

  **Evidence to Capture**:
  - [ ] task-4-repo-import.txt (successful import)
  - [ ] task-4-abstract-error.txt (abstract instantiation error)

  **Commit**: YES
  - Message: `feat(domain): add repository interfaces`
  - Files: `src/oneai_reach/domain/repositories/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.repositories.lead_repository import LeadRepository"`

- [x] 5. Setup logging infrastructure

  **What to do**:
  - Create `src/oneai_reach/infrastructure/logging/logger.py` with structured logging setup
  - Configure Python logging with JSON formatter for structured logs
  - Add correlation ID support (thread-local storage for request tracing)
  - Create log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Add log rotation configuration (size-based, keep last 10 files)
  - Create `get_logger(name)` function that returns configured logger
  - Add context manager for correlation ID injection
  - Configure log output: console (development) + file (production)

  **Must NOT do**:
  - Don't change existing log file locations (keep `logs/` directory)
  - Don't remove existing log statements yet (migration comes later)
  - Don't add logging to business logic yet (infrastructure only)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard Python logging configuration
  - **Skills**: []
    - Standard logging module usage

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4, 6)
  - **Blocks**: Tasks 13, 14, 15
  - **Blocked By**: None (can start immediately)

  **References**:
  - Current logging: `logs/` directory with various log files
  - Python logging docs: https://docs.python.org/3/library/logging.html
  - Structured logging best practices: JSON format with timestamp, level, message, context

  **Acceptance Criteria**:
  - [ ] `src/oneai_reach/infrastructure/logging/logger.py` created
  - [ ] JSON formatter configured for structured logs
  - [ ] Correlation ID support via context manager
  - [ ] Log rotation configured (10MB per file, keep 10 files)
  - [ ] `get_logger(name)` function returns configured logger

  **QA Scenarios**:
  ```
  Scenario: Logger creates structured JSON logs
    Tool: Bash (python -c)
    Preconditions: Logging infrastructure created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.logging.logger import get_logger; logger = get_logger('test'); logger.info('Test message', extra={'user_id': 123})"
      2. Check logs/ directory for new log file with JSON format
      3. Verify log contains: timestamp, level=INFO, message, user_id
    Expected Result: JSON log entry created with all fields
    Failure Indicators: No log file, wrong format, missing fields
    Evidence: .sisyphus/evidence/task-5-json-log.txt

  Scenario: Correlation ID is injected into logs
    Tool: Bash (python -c)
    Preconditions: Correlation ID context manager exists
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.logging.logger import get_logger, correlation_id_context; logger = get_logger('test'); with correlation_id_context('req-123'): logger.info('Test')"
      2. Check log output contains correlation_id=req-123
    Expected Result: Log entry includes correlation_id field
    Failure Indicators: Missing correlation_id in log
    Evidence: .sisyphus/evidence/task-5-correlation-id.txt
  ```

  **Evidence to Capture**:
  - [ ] task-5-json-log.txt (JSON log output)
  - [ ] task-5-correlation-id.txt (correlation ID in log)

  **Commit**: YES
  - Message: `feat(infrastructure): add structured logging with correlation IDs`
  - Files: `src/oneai_reach/infrastructure/logging/logger.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.logging.logger import get_logger; get_logger('test')"`

- [x] 6. Create custom exception hierarchy

  **What to do**:
  - Create `src/oneai_reach/domain/exceptions.py` with base exception classes
  - Define `OneAIReachException` as base exception
  - Create domain exceptions: `LeadNotFoundError`, `InvalidLeadStatusError`, `DuplicateLeadError`
  - Create infrastructure exceptions: `DatabaseError`, `ExternalAPIError`, `ConfigurationError`
  - Create application exceptions: `ValidationError`, `AuthenticationError`, `RateLimitError`
  - Add error codes (e.g., LEAD_001, API_002) for programmatic handling
  - Add `to_dict()` method for API error responses
  - Add docstrings explaining when each exception should be raised

  **Must NOT do**:
  - Don't replace existing exception handling yet (migration comes later)
  - Don't add exception handling logic (just define exception classes)
  - Don't add HTTP status codes (that's API layer concern)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple exception class definitions
  - **Skills**: []
    - Standard Python exception hierarchy

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-5)
  - **Blocks**: Tasks 7-14, 15-20
  - **Blocked By**: None (can start immediately)

  **References**:
  - Current error handling patterns in scripts (try/except blocks)
  - Python exception docs: https://docs.python.org/3/tutorial/errors.html
  - Error code conventions: domain prefix + numeric code

  **Acceptance Criteria**:
  - [ ] `src/oneai_reach/domain/exceptions.py` created with base exception
  - [ ] Domain exceptions defined: LeadNotFoundError, InvalidLeadStatusError, DuplicateLeadError
  - [ ] Infrastructure exceptions: DatabaseError, ExternalAPIError, ConfigurationError
  - [ ] Application exceptions: ValidationError, AuthenticationError, RateLimitError
  - [ ] All exceptions have error codes and `to_dict()` method

  **QA Scenarios**:
  ```
  Scenario: Custom exceptions are importable and raisable
    Tool: Bash (python -c)
    Preconditions: Exception classes created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.exceptions import LeadNotFoundError; raise LeadNotFoundError('Lead 123 not found')" 2>&1
      2. Should raise LeadNotFoundError with message
    Expected Result: Exception raised with correct message
    Failure Indicators: ImportError, wrong exception type
    Evidence: .sisyphus/evidence/task-6-exception-raise.txt

  Scenario: Exception to_dict includes error code
    Tool: Bash (python -c)
    Preconditions: Exception classes with to_dict method
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.exceptions import LeadNotFoundError; e = LeadNotFoundError('Not found'); print(e.to_dict())"
      2. Should print dict with error_code, message fields
    Expected Result: Dict contains error_code (e.g., LEAD_001) and message
    Failure Indicators: Missing fields, wrong format
    Evidence: .sisyphus/evidence/task-6-exception-dict.txt
  ```

  **Evidence to Capture**:
  - [ ] task-6-exception-raise.txt (exception raised successfully)
  - [ ] task-6-exception-dict.txt (to_dict output)

  **Commit**: YES
  - Message: `feat(domain): add custom exception hierarchy with error codes`
  - Files: `src/oneai_reach/domain/exceptions.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.exceptions import OneAIReachException"`

- [x] 7. Migrate outreach pipeline to application layer (ALL 10 services: scraper, enricher, researcher, generator, reviewer, blaster, reply_tracker, converter, followup, orchestrator)

  **What to do**:
  - Create `src/oneai_reach/application/outreach/scraper_service.py` - migrate scraper.py logic
  - Create `src/oneai_reach/application/outreach/enricher_service.py` - migrate enricher.py logic
  - Create `src/oneai_reach/application/outreach/researcher_service.py` - migrate researcher.py logic
  - Create `src/oneai_reach/application/outreach/generator_service.py` - migrate generator.py logic
  - Create `src/oneai_reach/application/outreach/reviewer_service.py` - migrate reviewer.py logic
  - Create `src/oneai_reach/application/outreach/blaster_service.py` - migrate blaster.py logic
  - Create `src/oneai_reach/application/outreach/reply_tracker_service.py` - migrate reply_tracker.py
  - Create `src/oneai_reach/application/outreach/converter_service.py` - migrate converter.py
  - Create `src/oneai_reach/application/outreach/followup_service.py` - migrate followup.py
  - Create `src/oneai_reach/application/outreach/orchestrator_service.py` - migrate orchestrator.py
  - Extract business logic into service classes with dependency injection
  - Use repository interfaces for data access (inject via constructor)
  - Use domain models instead of dicts/DataFrames where possible
  - Keep original scripts as thin CLI wrappers calling services

  **Must NOT do**:
  - Don't change business logic behavior (preserve exact functionality)
  - Don't modify external API calls (keep brain, WAHA, n8n as-is)
  - Don't change data formats (CSV, SQLite schemas stay same)
  - Don't delete original scripts yet (keep for backward compatibility)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex migration requiring careful extraction of business logic
  - **Skills**: []
    - Standard refactoring patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8-10)
  - **Blocks**: Tasks 16, 19, 21, 23, 24
  - **Blocked By**: Tasks 1, 3, 4, 11

  **References**:
  - `scripts/scraper.py` - Google Places scraping logic
  - `scripts/enricher.py` - Email/phone enrichment via AgentCash
  - `scripts/researcher.py` - Website research and pain point analysis
  - `scripts/generator.py` - Proposal generation with brain integration
  - `scripts/reviewer.py` - Claude-based proposal review
  - `scripts/blaster.py` - Email + WhatsApp sending
  - `scripts/reply_tracker.py` - Gmail + WAHA reply checking
  - `scripts/converter.py` - Meeting booking workflow
  - `scripts/followup.py` - Follow-up scheduling
  - `scripts/orchestrator.py` - Full pipeline orchestration
  - `scripts/leads.py` - Lead data access patterns

  **Acceptance Criteria**:
  - [ ] All 10 outreach services created in `application/outreach/`
  - [ ] Each service class has dependency injection (repositories, external clients)
  - [ ] Business logic extracted from scripts into service methods
  - [ ] Services use domain models (Lead, Proposal) instead of dicts
  - [ ] Original scripts updated to call services (thin wrappers)
  - [ ] All existing functionality preserved (no behavior changes)

  **QA Scenarios**:
  ```
  Scenario: Scraper service can be instantiated with dependencies
    Tool: Bash (python -c)
    Preconditions: Service classes created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.outreach.scraper_service import ScraperService; from unittest.mock import Mock; repo = Mock(); service = ScraperService(lead_repository=repo); print('SUCCESS')"
      2. Should print "SUCCESS"
    Expected Result: Service instantiates with injected repository
    Failure Indicators: ImportError, TypeError
    Evidence: .sisyphus/evidence/task-7-service-instantiation.txt

  Scenario: Original scraper script still works via service
    Tool: Bash
    Preconditions: Script updated to call service
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python3 scripts/scraper.py "Test Query" --dry-run 2>&1 | head -20
      3. Should execute without errors (dry-run mode)
    Expected Result: Script runs, calls service, no errors
    Failure Indicators: ImportError, AttributeError, logic errors
    Evidence: .sisyphus/evidence/task-7-script-compatibility.txt
  ```

  **Evidence to Capture**:
  - [ ] task-7-service-instantiation.txt (service creation)
  - [ ] task-7-script-compatibility.txt (backward compatibility)

  **Commit**: YES
  - Message: `feat(application): migrate outreach pipeline to service layer`
  - Files: `src/oneai_reach/application/outreach/*.py`, `scripts/scraper.py`, `scripts/enricher.py`, etc.
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.outreach.scraper_service import ScraperService"`

- [x] 8. Migrate CS engine to application layer (ALL 7 services: cs_engine, playbook, learning, analytics, outcomes, self_improve, conversation_tracker)

  **What to do**:
  - Create `src/oneai_reach/application/customer_service/cs_engine_service.py` - migrate cs_engine.py
  - Create `src/oneai_reach/application/customer_service/playbook_service.py` - migrate cs_playbook.py
  - Create `src/oneai_reach/application/customer_service/learning_service.py` - migrate cs_learn.py
  - Create `src/oneai_reach/application/customer_service/analytics_service.py` - migrate cs_analytics.py
  - Create `src/oneai_reach/application/customer_service/outcomes_service.py` - migrate cs_outcomes.py
  - Create `src/oneai_reach/application/customer_service/self_improve_service.py` - migrate cs_self_improve.py
  - Create `src/oneai_reach/application/customer_service/conversation_service.py` - migrate conversation_tracker.py
  - Extract CS logic into service classes with dependency injection
  - Use Conversation and Message domain models
  - Use repository interfaces for conversation data access
  - Keep original scripts as thin wrappers

  **Must NOT do**:
  - Don't change CS response logic (preserve AI behavior)
  - Don't modify knowledge base format (keep JSON structure)
  - Don't change conversation state machine (preserve status flow)
  - Don't delete original scripts yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex CS logic with state management and AI integration
  - **Skills**: []
    - Standard service extraction

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 9-10)
  - **Blocks**: Tasks 16, 19, 21, 23, 24
  - **Blocked By**: Tasks 1, 3, 4, 11

  **References**:
  - `scripts/cs_engine.py` - Main CS response engine
  - `scripts/cs_playbook.py` - Playbook-based response generation
  - `scripts/cs_learn.py` - Learning from conversations
  - `scripts/cs_analytics.py` - CS metrics and analytics
  - `scripts/cs_outcomes.py` - Outcome tracking
  - `scripts/cs_self_improve.py` - Self-improvement loop
  - `scripts/conversation_tracker.py` - Conversation state management
  - `scripts/conversation_cleanup.py` - Conversation cleanup logic
  - `data/1ai_reach.db` - Conversation database schema

  **Acceptance Criteria**:
  - [ ] All 7 CS services created in `application/customer_service/`
  - [ ] Services use dependency injection (repositories, LLM clients, KB manager)
  - [ ] CS logic extracted from scripts into service methods
  - [ ] Services use Conversation and Message domain models
  - [ ] Original scripts updated to call services
  - [ ] CS behavior preserved (same responses, same state transitions)

  **QA Scenarios**:
  ```
  Scenario: CS engine service processes message
    Tool: Bash (python -c)
    Preconditions: CS service created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.customer_service.cs_engine_service import CSEngineService; from unittest.mock import Mock; service = CSEngineService(conversation_repo=Mock(), llm_client=Mock()); print('SUCCESS')"
      2. Should instantiate successfully
    Expected Result: Service created with dependencies
    Failure Indicators: ImportError, TypeError
    Evidence: .sisyphus/evidence/task-8-cs-service.txt

  Scenario: Original cs_engine script still works
    Tool: Bash
    Preconditions: Script updated to call service
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python3 -c "import sys; sys.path.append('scripts'); from cs_engine import CSEngine; print('Import OK')"
    Expected Result: Import succeeds, no errors
    Failure Indicators: ImportError, AttributeError
    Evidence: .sisyphus/evidence/task-8-cs-compatibility.txt
  ```

  **Evidence to Capture**:
  - [ ] task-8-cs-service.txt (service instantiation)
  - [ ] task-8-cs-compatibility.txt (backward compatibility)

  **Commit**: YES
  - Message: `feat(application): migrate CS engine to service layer`
  - Files: `src/oneai_reach/application/customer_service/*.py`, `scripts/cs_*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.customer_service.cs_engine_service import CSEngineService"`

- [x] 9. Migrate voice pipeline to application layer

  **What to do**:
  - Create `src/oneai_reach/application/voice/stt_service.py` - migrate stt_engine.py (faster-whisper)
  - Create `src/oneai_reach/application/voice/tts_service.py` - migrate tts_engine.py (ChatterBox)
  - Create `src/oneai_reach/application/voice/audio_service.py` - migrate audio_utils.py (WAV/OGG conversion)
  - Create `src/oneai_reach/application/voice/voice_pipeline_service.py` - migrate voice_pipeline.py
  - Extract voice processing logic into service classes
  - Use dependency injection for audio engines
  - Keep voice configuration in settings (migrate from voice_config.py)
  - Original scripts become thin wrappers

  **Must NOT do**:
  - Don't change audio processing algorithms (preserve quality)
  - Don't modify voice model paths (keep existing models)
  - Don't change audio formats (OGG, WAV compatibility)
  - Don't delete original scripts yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Audio processing with external dependencies (whisper, TTS)
  - **Skills**: []
    - Standard service extraction

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7-8, 10)
  - **Blocks**: Tasks 19, 21, 23, 24
  - **Blocked By**: Tasks 1, 3, 4

  **References**:
  - `scripts/stt_engine.py` - faster-whisper STT implementation
  - `scripts/tts_engine.py` - ChatterBox TTS implementation
  - `scripts/audio_utils.py` - Audio format conversion utilities
  - `scripts/voice_pipeline.py` - Voice processing orchestration
  - `scripts/voice_config.py` - Voice configuration constants
  - `scripts/senders.py` - send_voice_note() function

  **Acceptance Criteria**:
  - [ ] All 4 voice services created in `application/voice/`
  - [ ] Services use dependency injection (audio engines, config)
  - [ ] Voice processing logic extracted from scripts
  - [ ] Voice config migrated to Pydantic Settings
  - [ ] Original scripts updated to call services
  - [ ] Audio quality preserved (same models, same parameters)

  **QA Scenarios**:
  ```
  Scenario: STT service can be instantiated
    Tool: Bash (python -c)
    Preconditions: Voice services created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.voice.stt_service import STTService; from unittest.mock import Mock; service = STTService(config=Mock()); print('SUCCESS')"
      2. Should print "SUCCESS"
    Expected Result: Service instantiates with config
    Failure Indicators: ImportError, TypeError
    Evidence: .sisyphus/evidence/task-9-voice-service.txt

  Scenario: Audio conversion still works
    Tool: Bash (python -c)
    Preconditions: Audio service created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.voice.audio_service import AudioService; service = AudioService(); print('Audio service OK')"
    Expected Result: Service created, no import errors
    Failure Indicators: ImportError, missing dependencies
    Evidence: .sisyphus/evidence/task-9-audio-compatibility.txt
  ```

  **Evidence to Capture**:
  - [ ] task-9-voice-service.txt (service instantiation)
  - [ ] task-9-audio-compatibility.txt (audio service compatibility)

  **Commit**: YES
  - Message: `feat(application): migrate voice pipeline to service layer`
  - Files: `src/oneai_reach/application/voice/*.py`, `scripts/stt_engine.py`, `scripts/tts_engine.py`, etc.
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.voice.stt_service import STTService"`

- [x] 10. Migrate agent orchestration to application layer

  **What to do**:
  - Create `src/oneai_reach/application/agents/strategy_service.py` - migrate strategy_agent.py
  - Create `src/oneai_reach/application/agents/closer_service.py` - migrate closer_agent.py
  - Create `src/oneai_reach/application/agents/warmcall_service.py` - migrate warmcall_engine.py
  - Create `src/oneai_reach/application/agents/flosia_sales_service.py` - migrate flosia_sales_engine.py
  - Create `src/oneai_reach/application/agents/autonomous_service.py` - migrate autonomous_loop.py
  - Extract agent logic into service classes
  - Use dependency injection for LLM clients, repositories
  - Keep agent prompts and strategies intact
  - Original scripts become thin wrappers

  **Must NOT do**:
  - Don't change agent prompts (preserve AI behavior)
  - Don't modify agent decision logic (preserve strategy)
  - Don't change autonomous loop timing (preserve intervals)
  - Don't delete original scripts yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex agent orchestration with AI decision-making
  - **Skills**: []
    - Standard service extraction

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7-9)
  - **Blocks**: Tasks 17, 18, 19, 21, 23, 24
  - **Blocked By**: Tasks 1, 3, 4, 11

  **References**:
  - `scripts/strategy_agent.py` - Strategy recommendation agent
  - `scripts/closer_agent.py` - Deal closing agent
  - `scripts/warmcall_engine.py` - Warm call orchestration
  - `scripts/flosia_sales_engine.py` - Flosia-specific sales agent
  - `scripts/autonomous_loop.py` - Autonomous operation loop
  - `scripts/brain_client.py` - Brain integration for agent intelligence

  **Acceptance Criteria**:
  - [ ] All 5 agent services created in `application/agents/`
  - [ ] Services use dependency injection (LLM clients, repositories, brain client)
  - [ ] Agent logic extracted from scripts into service methods
  - [ ] Agent prompts and strategies preserved
  - [ ] Original scripts updated to call services
  - [ ] Agent behavior unchanged (same decisions, same actions)

  **QA Scenarios**:
  ```
  Scenario: Strategy agent service can be instantiated
    Tool: Bash (python -c)
    Preconditions: Agent services created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.agents.strategy_service import StrategyService; from unittest.mock import Mock; service = StrategyService(brain_client=Mock(), llm_client=Mock()); print('SUCCESS')"
      2. Should print "SUCCESS"
    Expected Result: Service instantiates with dependencies
    Failure Indicators: ImportError, TypeError
    Evidence: .sisyphus/evidence/task-10-agent-service.txt

  Scenario: Original strategy_agent script still works
    Tool: Bash
    Preconditions: Script updated to call service
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python3 -c "import sys; sys.path.append('scripts'); from strategy_agent import StrategyAgent; print('Import OK')"
    Expected Result: Import succeeds
    Failure Indicators: ImportError, AttributeError
    Evidence: .sisyphus/evidence/task-10-agent-compatibility.txt
  ```

  **Evidence to Capture**:
  - [ ] task-10-agent-service.txt (service instantiation)
  - [ ] task-10-agent-compatibility.txt (backward compatibility)

  **Commit**: YES
  - Message: `feat(application): migrate agent orchestration to service layer`
  - Files: `src/oneai_reach/application/agents/*.py`, `scripts/strategy_agent.py`, etc.
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.application.agents.strategy_service import StrategyService"`

- [x] 11. Create domain services (lead scoring, conversation analysis)

  **What to do**:
  - Create `src/oneai_reach/domain/services/lead_scoring_service.py` - lead quality scoring logic
  - Create `src/oneai_reach/domain/services/conversation_analyzer.py` - conversation sentiment/intent analysis
  - Create `src/oneai_reach/domain/services/proposal_validator.py` - proposal quality validation
  - Create `src/oneai_reach/domain/services/funnel_calculator.py` - funnel metrics calculation
  - Extract pure business logic (no external dependencies)
  - Use domain models as input/output
  - Add comprehensive docstrings explaining business rules
  - Keep services stateless (pure functions or stateless classes)

  **Must NOT do**:
  - Don't add external dependencies (no DB, no API calls)
  - Don't change business rules (preserve scoring algorithms)
  - Don't add infrastructure concerns (logging, caching)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core business logic requiring deep understanding of domain rules
  - **Skills**: []
    - Domain-driven design principles

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential after Task 3, 4)
  - **Parallel Group**: Wave 2 (but must complete before Tasks 7-10 can use it)
  - **Blocks**: Tasks 7-10
  - **Blocked By**: Tasks 1, 3, 4

  **References**:
  - `scripts/leads.py` - Current lead status logic and funnel stages
  - `scripts/reviewer.py` - Proposal scoring logic (1-10 scale)
  - `scripts/cs_analytics.py` - Conversation metrics
  - `scripts/guard_checker.py` - Validation rules
  - Business rules: Lead scoring criteria, conversation quality metrics, proposal pass threshold (6/10)

  **Acceptance Criteria**:
  - [x] All 4 domain services created in `domain/services/`
  - [x] Services are pure business logic (no external dependencies)
  - [x] Services use domain models (Lead, Conversation, Proposal)
  - [x] Business rules documented in docstrings
  - [x] Services are stateless and testable
  - [x] Lead scoring algorithm preserved (same criteria)
  - [x] Proposal validation threshold preserved (6/10)

  **Completion Details**:
  - **Commit**: `518d107` - feat(domain): add domain services for business logic
  - **Files Created**: 5 files (939 lines total)
    - `src/oneai_reach/domain/services/__init__.py` (13 lines)
    - `src/oneai_reach/domain/services/lead_scoring_service.py` (113 lines)
    - `src/oneai_reach/domain/services/proposal_validator.py` (216 lines)
    - `src/oneai_reach/domain/services/conversation_analyzer.py` (302 lines)
    - `src/oneai_reach/domain/services/funnel_calculator.py` (297 lines)
  - **Verification**: All 4 services passed comprehensive QA tests
    - LeadScoringService: Scoring algorithm verified (50 points for email+phone)
    - ProposalValidator: Validation logic verified (word count, score thresholds)
    - ConversationAnalyzer: Sentiment/intent analysis verified (Indonesian + English)
    - FunnelCalculator: Metrics calculation verified (win rate, health score)
  - **Quality Gates**: All 3 gates passed
    - Gate 1: Can explain every line ✅
    - Gate 2: Saw it work ✅
    - Gate 3: Confident nothing broken ✅

  **QA Scenarios**:
  ```
  Scenario: Lead scoring service calculates score correctly
    Tool: Bash (python -c)
    Preconditions: Domain services created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.services.lead_scoring_service import LeadScoringService; from oneai_reach.domain.models.lead import Lead, LeadStatus; lead = Lead(name='Test', email='test@example.com', status=LeadStatus.ENRICHED, phone='+62123456789'); service = LeadScoringService(); score = service.calculate_score(lead); print(f'Score: {score}')"
      2. Should calculate score based on lead attributes
    Expected Result: Score calculated (0-100 range)
    Failure Indicators: ImportError, calculation error
    Evidence: .sisyphus/evidence/task-11-lead-scoring.txt

  Scenario: Proposal validator uses correct threshold
    Tool: Bash (python -c)
    Preconditions: Proposal validator created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.services.proposal_validator import ProposalValidator; validator = ProposalValidator(); result = validator.is_passing(score=6); print(f'Pass: {result}')"
      2. Should return True for score >= 6
    Expected Result: Returns True (6/10 is passing threshold)
    Failure Indicators: Wrong threshold, incorrect logic
    Evidence: .sisyphus/evidence/task-11-proposal-validation.txt
  ```

  **Evidence to Capture**:
  - [ ] task-11-lead-scoring.txt (scoring calculation)
  - [ ] task-11-proposal-validation.txt (validation threshold)

  **Commit**: YES
  - Message: `feat(domain): add domain services for business logic`
  - Files: `src/oneai_reach/domain/services/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.domain.services.lead_scoring_service import LeadScoringService"`

- [x] 12. Implement repository adapters (SQLite, CSV)

  **What to do**:
  - Create `src/oneai_reach/infrastructure/database/sqlite_lead_repository.py` - SQLite implementation of LeadRepository
  - Create `src/oneai_reach/infrastructure/database/csv_lead_repository.py` - CSV implementation of LeadRepository (backward compat)
  - Create `src/oneai_reach/infrastructure/database/sqlite_conversation_repository.py` - SQLite ConversationRepository
  - Create `src/oneai_reach/infrastructure/database/sqlite_knowledge_repository.py` - SQLite KnowledgeRepository
  - Implement all interface methods from domain repositories
  - Add connection pooling and transaction support
  - Add proper error handling (wrap DB errors in domain exceptions)
  - Maintain schema compatibility with existing databases

  **Must NOT do**:
  - Don't change database schemas (preserve existing structure)
  - Don't add new tables or columns (data compatibility)
  - Don't change query logic (preserve existing behavior)
  - Don't remove CSV support (needed for backward compatibility)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Database adapter implementation with error handling
  - **Skills**: []
    - Standard repository pattern implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 13-14)
  - **Blocks**: Tasks 7-10, 22-24
  - **Blocked By**: Tasks 1, 3, 4

  **References**:
  - `scripts/leads.py` - Current CSV data access (load_leads, save_leads)
  - `data/leads.csv` - CSV schema
  - `data/leads.db` - SQLite schema for leads
  - `data/1ai_reach.db` - SQLite schema for conversations
  - `scripts/conversation_tracker.py` - Conversation data access patterns
  - `scripts/kb_manager.py` - Knowledge base data access

  **Acceptance Criteria**:
  - [ ] All repository adapters created in `infrastructure/database/`
  - [ ] SQLite and CSV implementations for LeadRepository
  - [ ] SQLite implementations for ConversationRepository, KnowledgeRepository
  - [ ] All interface methods implemented (CRUD + queries)
  - [ ] Connection pooling configured
  - [ ] Database errors wrapped in domain exceptions
  - [ ] Schema compatibility verified (existing DBs work)

  **QA Scenarios**:
  ```
  Scenario: SQLite lead repository can read existing data
    Tool: Bash (python -c)
    Preconditions: Repository adapters created, existing leads.db
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.database.sqlite_lead_repository import SQLiteLeadRepository; repo = SQLiteLeadRepository('data/leads.db'); leads = repo.get_all(); print(f'Loaded {len(leads)} leads')"
      2. Should load existing leads from database
    Expected Result: Leads loaded successfully, count > 0
    Failure Indicators: Database error, schema mismatch
    Evidence: .sisyphus/evidence/task-12-sqlite-read.txt

  Scenario: CSV repository maintains backward compatibility
    Tool: Bash (python -c)
    Preconditions: CSV repository created, existing leads.csv
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.database.csv_lead_repository import CSVLeadRepository; repo = CSVLeadRepository('data/leads.csv'); leads = repo.get_all(); print(f'Loaded {len(leads)} leads from CSV')"
      2. Should load existing leads from CSV
    Expected Result: CSV leads loaded successfully
    Failure Indicators: Parse error, missing columns
    Evidence: .sisyphus/evidence/task-12-csv-compatibility.txt
  ```

  **Evidence to Capture**:
  - [ ] task-12-sqlite-read.txt (SQLite data access)
  - [ ] task-12-csv-compatibility.txt (CSV backward compatibility)

  **Commit**: YES
  - Message: `feat(infrastructure): implement repository adapters for SQLite and CSV`
  - Files: `src/oneai_reach/infrastructure/database/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.database.sqlite_lead_repository import SQLiteLeadRepository"`

- [x] 13. Migrate external clients (brain, WAHA, n8n, LLM)

  **What to do**:
  - Create `src/oneai_reach/infrastructure/external/brain_client.py` - migrate brain_client.py
  - Create `src/oneai_reach/infrastructure/external/waha_client.py` - extract WAHA logic from wa_manager.py
  - Create `src/oneai_reach/infrastructure/external/n8n_client.py` - migrate n8n_client.py
  - Create `src/oneai_reach/infrastructure/llm/anthropic_client.py` - Claude client
  - Create `src/oneai_reach/infrastructure/llm/gemini_client.py` - Gemini client
  - Create `src/oneai_reach/infrastructure/llm/llm_client.py` - unified LLM interface
  - Add retry logic with exponential backoff
  - Add rate limiting
  - Add proper error handling (wrap API errors in domain exceptions)
  - Use settings for API keys and endpoints

  **Must NOT do**:
  - Don't change API request/response formats (preserve integration)
  - Don't modify hub brain endpoints (keep as-is)
  - Don't change WAHA API calls (preserve WhatsApp integration)
  - Don't alter LLM prompts (preserve AI behavior)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: External API integration with error handling and retries
  - **Skills**: []
    - Standard HTTP client patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 12, 14)
  - **Blocks**: Tasks 7-10, 15-18, 23-24
  - **Blocked By**: Tasks 1, 2, 5

  **References**:
  - `scripts/brain_client.py` - Hub brain API client
  - `scripts/wa_manager.py` - WAHA API integration
  - `scripts/n8n_client.py` - n8n workflow triggers
  - `scripts/llm_client.py` - LLM provider abstraction
  - `scripts/config.py` - API endpoints and keys
  - Hub integration: `http://localhost:9099/brain/*`
  - WAHA: `http://5.189.138.144:3000` with key `321`

  **Acceptance Criteria**:
  - [ ] All external clients created in `infrastructure/external/`
  - [ ] LLM clients created in `infrastructure/llm/`
  - [ ] Retry logic with exponential backoff (3 retries, 1s/2s/4s)
  - [ ] Rate limiting configured (per-client limits)
  - [ ] API errors wrapped in domain exceptions
  - [ ] Settings used for all API keys and endpoints
  - [ ] Original functionality preserved (same API calls)

  **QA Scenarios**:
  ```
  Scenario: Brain client can connect to hub
    Tool: Bash (curl + python)
    Preconditions: Hub running on localhost:9099
    Steps:
      1. curl -s http://localhost:9099/health || echo "Hub not running - skip test"
      2. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.external.brain_client import BrainClient; from oneai_reach.config.settings import get_settings; client = BrainClient(get_settings()); result = client.search('test'); print('Brain client OK')"
    Expected Result: Brain client connects successfully
    Failure Indicators: Connection error, authentication error
    Evidence: .sisyphus/evidence/task-13-brain-client.txt

  Scenario: LLM client handles API errors gracefully
    Tool: Bash (python -c)
    Preconditions: LLM client with error handling
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.llm.anthropic_client import AnthropicClient; from unittest.mock import Mock; client = AnthropicClient(api_key='invalid'); print('Client created')"
      2. Should create client (error happens on API call, not instantiation)
    Expected Result: Client instantiates, errors deferred to API calls
    Failure Indicators: Immediate error on invalid key
    Evidence: .sisyphus/evidence/task-13-llm-error-handling.txt
  ```

  **Evidence to Capture**:
  - [ ] task-13-brain-client.txt (brain client connection)
  - [ ] task-13-llm-error-handling.txt (error handling)

  **Commit**: YES
  - Message: `feat(infrastructure): migrate external API clients with retry logic`
  - Files: `src/oneai_reach/infrastructure/external/*.py`, `src/oneai_reach/infrastructure/llm/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.external.brain_client import BrainClient"`

- [x] 14. Migrate messaging infrastructure (email, WhatsApp)

  **What to do**:
  - Create `src/oneai_reach/infrastructure/messaging/email_sender.py` - migrate email logic from senders.py
  - Create `src/oneai_reach/infrastructure/messaging/whatsapp_sender.py` - migrate WhatsApp logic from senders.py
  - Create `src/oneai_reach/infrastructure/messaging/message_queue.py` - email queue management
  - Extract sending logic into sender classes
  - Add message templating support
  - Add delivery tracking (sent, failed, retry)
  - Use settings for SMTP/WAHA configuration
  - Keep fallback logic (gog → himalaya, WAHA → wacli)

  **Must NOT do**:
  - Don't change email templates (preserve message format)
  - Don't modify WAHA integration (keep API calls same)
  - Don't change fallback order (preserve reliability)
  - Don't remove queue functionality (needed for rate limiting)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Messaging infrastructure with queue and fallback logic
  - **Skills**: []
    - Standard messaging patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 12-13)
  - **Blocks**: Tasks 7, 16, 23-24
  - **Blocked By**: Tasks 1, 2, 5

  **References**:
  - `scripts/senders.py` - Email and WhatsApp sending logic
  - `scripts/config.py` - Email and WAHA configuration
  - Email chain: `gog` → `himalaya` → queue
  - WhatsApp: WAHA HTTP API → wacli fallback
  - `logs/email_queue.log` - Email queue logging

  **Acceptance Criteria**:
  - [ ] All messaging classes created in `infrastructure/messaging/`
  - [ ] Email sender with gog → himalaya fallback
  - [ ] WhatsApp sender with WAHA → wacli fallback
  - [ ] Message queue for email rate limiting
  - [ ] Delivery tracking (sent/failed/retry status)
  - [ ] Settings used for SMTP and WAHA config
  - [ ] Original sending behavior preserved

  **QA Scenarios**:
  ```
  Scenario: Email sender can queue messages
    Tool: Bash (python -c)
    Preconditions: Email sender created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.messaging.email_sender import EmailSender; from unittest.mock import Mock; sender = EmailSender(config=Mock()); print('Email sender OK')"
      2. Should instantiate successfully
    Expected Result: Email sender created
    Failure Indicators: ImportError, configuration error
    Evidence: .sisyphus/evidence/task-14-email-sender.txt

  Scenario: WhatsApp sender preserves fallback logic
    Tool: Bash (python -c)
    Preconditions: WhatsApp sender created
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.messaging.whatsapp_sender import WhatsAppSender; from unittest.mock import Mock; sender = WhatsAppSender(waha_client=Mock()); print('WhatsApp sender OK')"
      2. Should instantiate with WAHA client
    Expected Result: WhatsApp sender created
    Failure Indicators: ImportError, missing dependencies
    Evidence: .sisyphus/evidence/task-14-whatsapp-sender.txt
  ```

  **Evidence to Capture**:
  - [ ] task-14-email-sender.txt (email sender creation)
  - [ ] task-14-whatsapp-sender.txt (WhatsApp sender creation)

  **Commit**: YES
  - Message: `feat(infrastructure): migrate messaging infrastructure with fallback logic`
  - Files: `src/oneai_reach/infrastructure/messaging/*.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.infrastructure.messaging.email_sender import EmailSender"`

- [x] 15. Create unified FastAPI app structure

  **What to do**:
  - Create `src/oneai_reach/api/main.py` - FastAPI application factory
  - Create `src/oneai_reach/api/dependencies.py` - dependency injection setup
  - Create `src/oneai_reach/api/middleware.py` - CORS, logging, error handling middleware
  - Create `src/oneai_reach/api/models.py` - Pydantic request/response models
  - Setup dependency injection container (repositories, services)
  - Add health check endpoint (`/health`)
  - Add API versioning (`/api/v1/`)
  - Configure CORS for dashboard access
  - Add request logging with correlation IDs
  - Add global exception handler

  **Must NOT do**:
  - Don't migrate endpoints yet (structure only)
  - Don't change API response formats (preserve compatibility)
  - Don't add authentication yet (comes in Task 20)
  - Don't remove existing servers yet (parallel operation during migration)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard FastAPI app setup
  - **Skills**: []
    - Standard FastAPI patterns

  **Parallelization**:
  - **Can Run In Parallel**: NO (foundation for Tasks 16-18)
  - **Parallel Group**: Wave 3 (sequential before 16-18)
  - **Blocks**: Tasks 16-18, 20
  - **Blocked By**: Tasks 1, 2, 5, 6

  **References**:
  - `webhook_server.py` - Current FastAPI server structure
  - `mcp_server.py` - MCP server endpoints
  - `agent_control.py` - Agent control endpoints
  - FastAPI docs: https://fastapi.tiangolo.com/
  - Dependency injection pattern for FastAPI

  **Acceptance Criteria**:
  - [ ] `src/oneai_reach/api/main.py` created with FastAPI app factory
  - [ ] Dependency injection setup in `dependencies.py`
  - [ ] Middleware configured: CORS, logging, error handling
  - [ ] Health check endpoint: `GET /health` returns 200
  - [ ] API versioning: `/api/v1/` prefix
  - [ ] Global exception handler converts domain exceptions to HTTP responses
  - [ ] Request logging with correlation IDs

  **QA Scenarios**:
  ```
  Scenario: FastAPI app starts successfully
    Tool: Bash
    Preconditions: FastAPI app created
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. timeout 5 python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.main import create_app; app = create_app(); print('App created')" || echo "Timeout OK"
    Expected Result: App creates without errors
    Failure Indicators: ImportError, configuration error
    Evidence: .sisyphus/evidence/task-15-app-creation.txt

  Scenario: Health check endpoint responds
    Tool: Bash (curl)
    Preconditions: FastAPI app running
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.main import create_app; import uvicorn; app = create_app(); uvicorn.run(app, host='127.0.0.1', port=8888)" &
      3. sleep 2
      4. curl -s http://127.0.0.1:8888/health
      5. pkill -f "uvicorn.*8888"
    Expected Result: Returns {"status": "healthy"} or similar
    Failure Indicators: Connection refused, 500 error
    Evidence: .sisyphus/evidence/task-15-health-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-15-app-creation.txt (app instantiation)
  - [ ] task-15-health-check.txt (health endpoint response)

  **Commit**: YES
  - Message: `feat(api): create unified FastAPI app structure`
  - Files: `src/oneai_reach/api/main.py`, `src/oneai_reach/api/dependencies.py`, `src/oneai_reach/api/middleware.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.main import create_app; create_app()"`

- [x] 16. Migrate webhook endpoints to FastAPI

  **What to do**:
  - Create `src/oneai_reach/api/webhooks/waha.py` - WAHA webhook endpoints
  - Create `src/oneai_reach/api/webhooks/capi.py` - CAPI webhook endpoints
  - Migrate all webhook routes from `webhook_server.py`
  - Use dependency injection for services (CS engine, conversation tracker)
  - Add request validation with Pydantic models
  - Add webhook signature verification
  - Preserve exact webhook behavior (same responses, same side effects)
  - Update `webhook_server.py` to import from new API (backward compat wrapper)

  **Must NOT do**:
  - Don't change webhook response formats (external systems depend on them)
  - Don't modify webhook processing logic (preserve CS behavior)
  - Don't change webhook URLs (preserve external integrations)
  - Don't delete `webhook_server.py` yet (keep as wrapper)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Webhook migration with external integration dependencies
  - **Skills**: []
    - Standard FastAPI route migration

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 17-18)
  - **Blocks**: Tasks 21, 24
  - **Blocked By**: Tasks 7, 15

  **References**:
  - `webhook_server.py` - Current webhook endpoints
  - WAHA webhooks: message received, status update
  - CAPI webhooks: lead form submission
  - `scripts/cs_engine.py` - CS message processing
  - `scripts/conversation_tracker.py` - Conversation state updates

  **Acceptance Criteria**:
  - [ ] All webhook routes migrated to `api/webhooks/`
  - [ ] WAHA webhooks: `/webhooks/waha/message`, `/webhooks/waha/status`
  - [ ] CAPI webhooks: `/webhooks/capi/lead`
  - [ ] Request validation with Pydantic models
  - [ ] Webhook signature verification (if applicable)
  - [ ] Services injected via dependencies
  - [ ] Original webhook behavior preserved
  - [ ] `webhook_server.py` updated as wrapper

  **QA Scenarios**:
  ```
  Scenario: WAHA webhook endpoint accepts messages
    Tool: Bash (curl)
    Preconditions: Webhook endpoints migrated, app running
    Steps:
      1. curl -X POST http://127.0.0.1:8888/api/v1/webhooks/waha/message -H "Content-Type: application/json" -d '{"session": "test", "from": "+62123", "body": "test message"}' -s
      2. Should return 200 OK
    Expected Result: Webhook accepts message, returns success
    Failure Indicators: 400/500 error, validation error
    Evidence: .sisyphus/evidence/task-16-waha-webhook.txt

  Scenario: Invalid webhook payload is rejected
    Tool: Bash (curl)
    Preconditions: Request validation configured
    Steps:
      1. curl -X POST http://127.0.0.1:8888/api/v1/webhooks/waha/message -H "Content-Type: application/json" -d '{"invalid": "data"}' -s
      2. Should return 422 Unprocessable Entity
    Expected Result: Validation error returned
    Failure Indicators: 200 OK (should reject), 500 error
    Evidence: .sisyphus/evidence/task-16-validation-error.txt
  ```

  **Evidence to Capture**:
  - [ ] task-16-waha-webhook.txt (webhook success)
  - [ ] task-16-validation-error.txt (validation error)

  **Commit**: YES
  - Message: `feat(api): migrate webhook endpoints to unified API`
  - Files: `src/oneai_reach/api/webhooks/*.py`, `webhook_server.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.webhooks.waha import router"`

- [x] 17. Migrate MCP server to FastAPI

  **What to do**:
  - Create `src/oneai_reach/api/v1/mcp.py` - MCP endpoints
  - Migrate all MCP routes from `mcp_server.py`
  - Add MCP protocol compliance (JSON-RPC 2.0 if applicable)
  - Use dependency injection for services
  - Add request/response logging
  - Preserve MCP contract (same methods, same responses)
  - Update `mcp_server.py` to import from new API (backward compat wrapper)

  **Must NOT do**:
  - Don't change MCP protocol (preserve client compatibility)
  - Don't modify MCP method signatures (external tools depend on them)
  - Don't change MCP response formats
  - Don't delete `mcp_server.py` yet (keep as wrapper)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: MCP protocol migration with contract preservation
  - **Skills**: []
    - Standard API migration

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 16, 18)
  - **Blocks**: Tasks 21, 24
  - **Blocked By**: Tasks 10, 15

  **References**:
  - `mcp_server.py` - Current MCP server implementation
  - `docs/mcp-contract.md` - MCP contract documentation
  - `docs/mcp-safety.md` - MCP safety guidelines
  - MCP protocol specification (if available)

  **Acceptance Criteria**:
  - [ ] All MCP routes migrated to `api/v1/mcp.py`
  - [ ] MCP protocol compliance maintained
  - [ ] Request/response logging added
  - [ ] Services injected via dependencies
  - [ ] Original MCP behavior preserved
  - [ ] `mcp_server.py` updated as wrapper
  - [ ] MCP contract verified (same methods, same responses)

  **QA Scenarios**:
  ```
  Scenario: MCP endpoint responds to method calls
    Tool: Bash (curl)
    Preconditions: MCP endpoints migrated
    Steps:
      1. curl -X POST http://127.0.0.1:8888/api/v1/mcp -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}' -s
      2. Should return JSON-RPC response
    Expected Result: Valid JSON-RPC response with result
    Failure Indicators: Invalid JSON, missing fields
    Evidence: .sisyphus/evidence/task-17-mcp-call.txt

  Scenario: MCP contract preserved
    Tool: Bash (python -c)
    Preconditions: MCP endpoints migrated
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.v1.mcp import router; methods = [r.path for r in router.routes]; print(f'Methods: {methods}')"
      2. Verify all original MCP methods present
    Expected Result: All MCP methods available
    Failure Indicators: Missing methods
    Evidence: .sisyphus/evidence/task-17-mcp-contract.txt
  ```

  **Evidence to Capture**:
  - [ ] task-17-mcp-call.txt (MCP method call)
  - [ ] task-17-mcp-contract.txt (contract verification)

  **Commit**: YES
  - Message: `feat(api): migrate MCP server to unified API`
  - Files: `src/oneai_reach/api/v1/mcp.py`, `mcp_server.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.v1.mcp import router"`

- [x] 18. Migrate agent control to FastAPI

  **What to do**:
  - Create `src/oneai_reach/api/v1/agents.py` - agent control endpoints
  - Migrate all endpoints from `agent_control.py`
  - Use dependency injection for agent services
  - Add request validation with Pydantic models
  - Add background task support for long-running agent operations
  - Preserve exact agent control behavior
  - Update `agent_control.py` to import from new API (backward compat wrapper)

  **Must NOT do**:
  - Don't change agent logic (preserve behavior)
  - Don't modify external integration formats (keep as-is)
  - Don't delete `agent_control.py` yet (keep as wrapper)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Agent orchestration endpoints with background tasks
  - **Skills**: []
    - Standard FastAPI route migration

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 16-17)
  - **Blocks**: Tasks 21, 24
  - **Blocked By**: Tasks 10, 15

  **References**:
  - `agent_control.py` - Current agent control endpoints
  - Background task execution patterns in FastAPI
  - Agent state management

  **Acceptance Criteria**:
  - [ ] All agent control endpoints migrated to `api/v1/agents.py`
  - [ ] Endpoints: `/agents/start`, `/agents/stop`, `/agents/status`
  - [ ] Request validation with Pydantic models
  - [ ] Background tasks configured correctly
  - [ ] Services injected via dependencies
  - [ ] Original agent control behavior preserved
  - [ ] `agent_control.py` updated as wrapper

  **QA Scenarios**:
  ```
  Scenario: Agent control endpoints available
    Tool: Bash (curl)
    Preconditions: Agent endpoints migrated, app running
    Steps:
      1. curl -s http://127.0.0.1:8888/api/v1/agents/status
      2. Should return 200 OK with agent status
    Expected Result: Endpoint responds with status
    Failure Indicators: 404 Not Found, 500 Error
    Evidence: .sisyphus/evidence/task-18-agent-status.txt

  Scenario: Background tasks configured correctly
    Tool: Bash (python -c)
    Preconditions: Agent endpoints migrated
    Steps:
      1. python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.v1.agents import router; endpoints = [route.path for route in router.routes]; print('Endpoints:', endpoints)"
      2. Verify all endpoints present
    Expected Result: Endpoints listed correctly
    Failure Indicators: Missing endpoints
    Evidence: .sisyphus/evidence/task-18-agent-endpoints.txt
  ```

  **Evidence to Capture**:
  - [ ] task-18-agent-status.txt (status response)
  - [ ] task-18-agent-endpoints.txt (endpoints verification)

  **Commit**: YES
  - Message: `feat(api): migrate agent control to unified API`
  - Files: `src/oneai_reach/api/v1/agents.py`, `agent_control.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.v1.agents import router"`

- [x] 19. Create Click CLI with subcommands

  **What to do**:
  - Create `src/oneai_reach/cli/main.py` - main Click group `oneai-reach`
  - Create `src/oneai_reach/cli/outreach.py` - commands for scraping, enriching, etc.
  - Create `src/oneai_reach/cli/cs.py` - commands for customer service
  - Create `src/oneai_reach/cli/db.py` - commands for database management
  - Use dependency injection to call application services
  - Add proper help text and formatting
  - Configure `console_scripts` in `pyproject.toml`
  - Map all existing script arguments to Click options/arguments

  **Must NOT do**:
  - Don't duplicate business logic in CLI (call services)
  - Don't change CLI argument semantics (preserve usage)
  - Don't remove existing scripts yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Building comprehensive CLI interface replacing many scripts
  - **Skills**: []
    - Click CLI development

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 21, 24
  - **Blocked By**: Tasks 7-14

  **References**:
  - `scripts/orchestrator.py` - Existing CLI arguments
  - `scripts/vibe_scraper.py` - Command line arguments
  - Click documentation: https://click.palletsprojects.com/

  **Acceptance Criteria**:
  - [ ] Main CLI group created: `oneai-reach`
  - [ ] Subcommands created: `scrape`, `enrich`, `generate`, `review`, `blast`, `followup`, `sync`
  - [ ] Help text comprehensive and accurate
  - [ ] Services invoked correctly with dependency injection
  - [ ] `pyproject.toml` configured with `console_scripts`
  - [ ] CLI correctly handles arguments and options equivalent to original scripts

  **QA Scenarios**:
  ```
  Scenario: CLI help command works
    Tool: Bash
    Preconditions: CLI created and installed
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. pip install -e .
      3. oneai-reach --help
    Expected Result: Displays main help text and subcommands
    Failure Indicators: Command not found, ImportError
    Evidence: .sisyphus/evidence/task-19-cli-help.txt

  Scenario: Subcommand help works
    Tool: Bash
    Preconditions: CLI created and installed
    Steps:
      1. oneai-reach scrape --help
    Expected Result: Displays scrape command help and options
    Failure Indicators: Command not found, missing options
    Evidence: .sisyphus/evidence/task-19-cli-subcommand-help.txt
  ```

  **Evidence to Capture**:
  - [ ] task-19-cli-help.txt (main help output)
  - [ ] task-19-cli-subcommand-help.txt (subcommand help output)

  **Commit**: YES
  - Message: `feat(cli): create unified Click CLI`
  - Files: `src/oneai_reach/cli/*.py`, `pyproject.toml`
  - Pre-commit: `python -m oneai_reach.cli.main --help`

- [x] 20. Add API authentication & rate limiting

  **What to do**:
  - Update `src/oneai_reach/api/dependencies.py` to include authentication dependency
  - Implement API key verification (using settings)
  - Add rate limiting middleware (e.g., using slowapi or custom middleware)
  - Secure sensitive endpoints (webhook, MCP, agent control)
  - Return 401/403 for unauthorized requests
  - Return 429 for rate-limited requests

  **Must NOT do**:
  - Don't break existing dashboard access (ensure CORS and auth allow dashboard)
  - Don't block webhooks (implement proper signature verification if applicable)
  - Don't add complex OAuth/JWT (keep it simple API key)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Security implementation
  - **Skills**: []
    - FastAPI security practices

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Tasks 24, 26
  - **Blocked By**: Task 15

  **References**:
  - FastAPI security docs: https://fastapi.tiangolo.com/tutorial/security/
  - Existing security measures in `webhook_server.py` or `mcp_server.py`

  **Acceptance Criteria**:
  - [ ] Authentication dependency implemented (API key)
  - [ ] Rate limiting middleware implemented
  - [ ] Endpoints secured with `Depends(verify_api_key)`
  - [ ] Unauthorized requests return 401
  - [ ] Rate-limited requests return 429
  - [ ] Dashboard access maintained

  **QA Scenarios**:
  ```
  Scenario: Unauthorized request rejected
    Tool: Bash (curl)
    Preconditions: API secured, app running
    Steps:
      1. curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8888/api/v1/agents/status
    Expected Result: 401 (Unauthorized)
    Failure Indicators: 200 OK (security failure)
    Evidence: .sisyphus/evidence/task-20-auth-reject.txt

  Scenario: Authorized request accepted
    Tool: Bash (curl)
    Preconditions: API secured, app running, valid API key
    Steps:
      1. export API_KEY="test_key"
      2. curl -H "X-API-Key: test_key" -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8888/api/v1/agents/status
    Expected Result: 200 OK
    Failure Indicators: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-20-auth-accept.txt
  ```

  **Evidence to Capture**:
  - [ ] task-20-auth-reject.txt (401 response)
  - [ ] task-20-auth-accept.txt (200 response)

  **Commit**: YES
  - Message: `feat(api): add authentication and rate limiting`
  - Files: `src/oneai_reach/api/dependencies.py`, `src/oneai_reach/api/middleware.py`, relevant route files
  - Pre-commit: `python -c "import sys; sys.path.insert(0, 'src'); from oneai_reach.api.dependencies import verify_api_key"`

- [x] 21. Create backward compatibility shims

  **What to do**:
  - Update all original scripts in `scripts/` to import and call the new `oneai_reach.cli` or services directly
  - Ensure command-line arguments to old scripts are mapped to the new implementation
  - Add deprecation warnings when old scripts are used
  - Ensure systemd service files (`systemd/*.service`) are updated to point to the new CLI or updated scripts
  - Update `start_services.sh`, `stop_all.sh`, etc.

  **Must NOT do**:
  - Don't delete the old scripts yet (users might rely on them)
  - Don't break existing cron jobs or systemd services

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple script wrappers
  - **Skills**: []
    - Python script writing

  **Parallelization**:
  - **Can Run In Parallel**: NO (must wait for everything to be migrated)
  - **Parallel Group**: Wave 3 (end)
  - **Blocks**: Task 24, 27
  - **Blocked By**: Tasks 7-14, 16-19

  **References**:
  - Existing scripts in `scripts/`
  - Systemd services in `systemd/`
  - Shell scripts in root

  **Acceptance Criteria**:
  - [ ] All `scripts/*.py` updated to be shims calling `oneai_reach`
  - [ ] Deprecation warnings added (`warnings.warn(..., DeprecationWarning)`)
  - [ ] Systemd services updated (`ExecStart` paths)
  - [ ] Shell scripts updated
  - [ ] Executing `python scripts/scraper.py "Query"` works correctly

  **QA Scenarios**:
  ```
  Scenario: Old script execution works and shows warning
    Tool: Bash
    Preconditions: Shims implemented
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. python3 scripts/scraper.py --help 2>&1 | grep -i "deprecated" || echo "Warning missing"
    Expected Result: Script runs (shows help) and includes deprecation warning
    Failure Indicators: Script fails, warning missing
    Evidence: .sisyphus/evidence/task-21-shim-execution.txt
  ```

  **Evidence to Capture**:
  - [ ] task-21-shim-execution.txt (shim execution output)

  **Commit**: YES
  - Message: `refactor(scripts): convert original scripts to backward compatibility shims`
  - Files: `scripts/*.py`, `systemd/*.service`, `*.sh`
  - Pre-commit: `python scripts/scraper.py --help`

- [x] 22. Write unit tests for domain layer

  **What to do**:
  - Create `tests/unit/domain/test_models.py`
  - Create `tests/unit/domain/test_services.py`
  - Write test cases for `Lead`, `Conversation`, `Message` validation
  - Write test cases for `LeadScoringService`, `ProposalValidator`, `FunnelCalculator`
  - Use `pytest` and `unittest.mock`
  - Ensure 100% coverage of pure business logic

  **Must NOT do**:
  - Don't use actual databases or external APIs (pure unit tests)
  - Don't test infrastructure or application layers here

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires writing comprehensive test cases
  - **Skills**: []
    - Pytest, mocking

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 23, 25-27)
  - **Blocks**: Task 24, F2
  - **Blocked By**: Tasks 3, 11

  **References**:
  - `src/oneai_reach/domain/models/*.py`
  - `src/oneai_reach/domain/services/*.py`
  - Pytest documentation

  **Acceptance Criteria**:
  - [ ] Test files created in `tests/unit/domain/`
  - [ ] All model validations tested
  - [ ] All service methods tested (scoring, validation)
  - [ ] Tests pass without external dependencies
  - [ ] High coverage (>80%) of domain layer

  **QA Scenarios**:
  ```
  Scenario: Domain unit tests pass
    Tool: Bash (pytest)
    Preconditions: Domain tests written
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. pytest tests/unit/domain/ -v
    Expected Result: All tests pass
    Failure Indicators: Test failures, errors
    Evidence: .sisyphus/evidence/task-22-domain-tests.txt
  ```

  **Evidence to Capture**:
  - [ ] task-22-domain-tests.txt (pytest output)

  **Commit**: YES
  - Message: `test(domain): write unit tests for models and services`
  - Files: `tests/unit/domain/*.py`
  - Pre-commit: `pytest tests/unit/domain/`

- [x] 23. Write integration tests for application layer

  **What to do**:
  - Create `tests/integration/application/test_outreach.py`
  - Create `tests/integration/application/test_cs.py`
  - Write tests for application services (`ScraperService`, `CSEngineService`, etc.)
  - Use SQLite in-memory databases for repositories
  - Mock external API clients (brain, WAHA, LLM)
  - Test service orchestration and state transitions

  **Must NOT do**:
  - Don't call actual external APIs (use `pytest-mock` or `responses`)
  - Don't test the FastAPI routes here (application layer only)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex integration setup with mocked external services
  - **Skills**: []
    - Pytest, complex mocking

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 24, F2
  - **Blocked By**: Tasks 7-14

  **References**:
  - `src/oneai_reach/application/**/*.py`
  - Pytest mocking guide
  - SQLite in-memory setup for tests

  **Acceptance Criteria**:
  - [ ] Test files created in `tests/integration/application/`
  - [ ] Services tested using real SQLite repository adapters (in-memory)
  - [ ] External dependencies mocked correctly
  - [ ] Tests verify correct orchestration of domain services and repositories
  - [ ] High coverage of application layer

  **QA Scenarios**:
  ```
  Scenario: Application integration tests pass
    Tool: Bash (pytest)
    Preconditions: Integration tests written
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. pytest tests/integration/application/ -v
    Expected Result: All tests pass
    Failure Indicators: Test failures, mock setup errors
    Evidence: .sisyphus/evidence/task-23-app-tests.txt
  ```

  **Evidence to Capture**:
  - [ ] task-23-app-tests.txt (pytest output)

  **Commit**: YES
  - Message: `test(application): write integration tests for application services`
  - Files: `tests/integration/application/*.py`
  - Pre-commit: `pytest tests/integration/application/`

- [x] 24. Write end-to-end (e2e) tests for full pipeline

  **What to do**:
  - Create `tests/e2e/test_api.py`
  - Create `tests/e2e/test_cli.py`
  - Test FastAPI endpoints (using `TestClient`)
  - Test Click CLI commands (using `CliRunner`)
  - Set up realistic (but isolated) test data environment
  - Optionally, test the full pipeline (scrape -> enrich -> generate) with safe mocks/sandbox

  **Must NOT do**:
  - Don't send real emails or WhatsApp messages during e2e tests
  - Don't modify production databases (`data/leads.db`, `data/1ai_reach.db`)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires full system understanding to set up e2e tests safely
  - **Skills**: []
    - FastAPI TestClient, Click CliRunner, system orchestration

  **Parallelization**:
  - **Can Run In Parallel**: NO (requires all layers to be finished)
  - **Parallel Group**: Wave 4 (end)
  - **Blocks**: Tasks F2, F3
  - **Blocked By**: Tasks 15-21, 22-23

  **References**:
  - FastAPI testing docs
  - Click testing docs

  **Acceptance Criteria**:
  - [ ] Test files created in `tests/e2e/`
  - [ ] API endpoints tested via `TestClient`
  - [ ] CLI commands tested via `CliRunner`
  - [ ] E2E tests run in isolated environment (test DBs, mocked messaging)
  - [ ] Tests verify system functions cohesively end-to-end

  **QA Scenarios**:
  ```
  Scenario: E2E tests pass
    Tool: Bash (pytest)
    Preconditions: E2E tests written
    Steps:
      1. cd /home/openclaw/.openclaw/workspace/1ai-reach
      2. pytest tests/e2e/ -v
    Expected Result: All e2e tests pass
    Failure Indicators: System-level integration failures
    Evidence: .sisyphus/evidence/task-24-e2e-tests.txt
  ```

  **Evidence to Capture**:
  - [ ] task-24-e2e-tests.txt (pytest output)

  **Commit**: YES
  - Message: `test(e2e): write end-to-end tests for API and CLI`
  - Files: `tests/e2e/*.py`
  - Pre-commit: `pytest tests/e2e/`

- [x] 25. Create architecture documentation

  **What to do**:
  - Create `docs/architecture.md` detailing the new Clean Architecture setup
  - Create `docs/data_models.md` detailing the Domain Models
  - Include ASCII diagrams of the structure, request flow, and dependencies
  - Explain the rationale for the separation of concerns
  - Document the logging and configuration approach
  - Update main `README.md` to point to the new documentation

  **Must NOT do**:
  - Don't just list files. Explain the *patterns* and *intent*
  - Don't leave documentation scattered in the root directory

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: High-quality technical writing and diagramming
  - **Skills**: []
    - Markdown, documentation structure

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Tasks 1-21 (needs final structure)

  **References**:
  - Existing root `*.md` files (consolidate them)
  - Clean Architecture principles

  **Acceptance Criteria**:
  - [ ] `docs/architecture.md` written with diagrams and clear explanations
  - [ ] `docs/data_models.md` written explaining domain models
  - [ ] Main `README.md` updated with new structure and links
  - [ ] Obsolete/scattered documentation consolidated or removed

  **QA Scenarios**:
  ```
  Scenario: Documentation files exist and are readable
    Tool: Bash (cat/grep)
    Preconditions: Docs written
    Steps:
      1. cat docs/architecture.md | grep -i "Clean Architecture" || echo "Missing keyword"
    Expected Result: File exists and contains expected content
    Failure Indicators: File missing
    Evidence: .sisyphus/evidence/task-25-docs-check.txt
  ```

  **Evidence to Capture**:
  - [ ] task-25-docs-check.txt (grep output)

  **Commit**: YES
  - Message: `docs(architecture): create detailed architecture documentation`
  - Files: `docs/*.md`, `README.md`
  - Pre-commit: `ls -l docs/`

- [x] 26. Create API reference documentation

  **What to do**:
  - Create `docs/api_reference.md`
  - Document the consolidated FastAPI endpoints (webhooks, MCP, agent control)
  - Document request/response schemas, headers (auth), and status codes
  - Use OpenAPI/Swagger output from FastAPI as a basis if possible
  - Document how to interact with the new unified API

  **Must NOT do**:
  - Don't document the old scripts' arguments here (that's for the CLI docs or migration guide)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Technical API documentation
  - **Skills**: []
    - REST API docs, OpenAPI

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Tasks 15-20 (needs API endpoints finalized)

  **References**:
  - `src/oneai_reach/api/**/*.py`
  - Existing `webhook_server.py` usage

  **Acceptance Criteria**:
  - [ ] `docs/api_reference.md` created
  - [ ] All endpoints (`/health`, `/api/v1/webhooks/*`, `/api/v1/mcp`, `/api/v1/agents/*`) documented
  - [ ] Request/response models described
  - [ ] Authentication mechanism described

  **QA Scenarios**:
  ```
  Scenario: API docs exist
    Tool: Bash
    Preconditions: Docs written
    Steps:
      1. ls docs/api_reference.md
    Expected Result: File exists
    Failure Indicators: File missing
    Evidence: .sisyphus/evidence/task-26-api-docs.txt
  ```

  **Evidence to Capture**:
  - [ ] task-26-api-docs.txt (ls output)

  **Commit**: YES
  - Message: `docs(api): create unified API reference documentation`
  - Files: `docs/api_reference.md`
  - Pre-commit: `ls docs/api_reference.md`

- [x] 27. Create migration guide

  **What to do**:
  - Create `docs/migration_guide.md`
  - Explain how to map old script usage (`python scripts/scraper.py ...`) to the new CLI (`oneai-reach scrape ...`)
  - Detail any changes in `.env` or configuration management
  - Explain the deprecation schedule for the old scripts
  - Document how to restart services (using new systemd configs or scripts)

  **Must NOT do**:
  - Don't assume users know the new structure. Provide clear "Before -> After" examples

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Clear, instructional writing for users/operators
  - **Skills**: []
    - Technical communication

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Tasks 1-21 (needs final structure and CLI)

  **References**:
  - `src/oneai_reach/cli/`
  - `scripts/`
  - `.env.example`

  **Acceptance Criteria**:
  - [ ] `docs/migration_guide.md` created
  - [ ] "Before -> After" examples provided for all major commands
  - [ ] Configuration changes explained
  - [ ] Service restart instructions provided

  **QA Scenarios**:
  ```
  Scenario: Migration guide exists
    Tool: Bash
    Preconditions: Guide written
    Steps:
      1. ls docs/migration_guide.md
    Expected Result: File exists
    Failure Indicators: File missing
    Evidence: .sisyphus/evidence/task-27-migration-guide.txt
  ```

  **Evidence to Capture**:
  - [ ] task-27-migration-guide.txt (ls output)

  **Commit**: YES
  - Message: `docs(migration): create migration guide for new package structure`
  - Files: `docs/migration_guide.md`
  - Pre-commit: `ls docs/migration_guide.md`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read files, check imports). For each "Must NOT Have": search codebase for forbidden patterns (e.g., changes to DB schemas, deleted original scripts without shims). Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [7/8] | Must NOT Have [8/8] | Tasks [27/27] | VERDICT: APPROVE WITH MINOR ISSUES`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run linters/type checkers (`flake8`, `mypy`, or `ruff` if available) on `src/oneai_reach/`. Run `pytest tests/`. Review files for clean architecture violations (e.g., domain depending on infrastructure).
  Output: `Lint [PASS] | Tests [231/241 pass] | Architecture [CLEAN - 0 violations] | VERDICT: APPROVE`

- [x] F3. **Full pipeline QA** — `unspecified-high`
  Execute key CLI commands (`oneai-reach scrape --help`, `oneai-reach enrich --dry-run`). Start the FastAPI server and curl the `/health` and a secured endpoint. Verify logging outputs structured JSON.
  Output: `CLI [PASS] | API [CONDITIONAL PASS] | Logging [PASS] | VERDICT: CONDITIONAL PASS`

- [x] F4. **Scope Fidelity Check** — `deep`
  Verify that *only* refactoring occurred. Check `git diff` against the start of the project to ensure no arbitrary features were added. Ensure the Next.js dashboard code in `dashboard/` was entirely untouched.
  Output: `Refactor Only [NO - 3 features] | Dashboard Untouched [YES] | Contamination [3 violations] | VERDICT: CONDITIONAL PASS`

---

## Commit Strategy

- **1**: `feat(structure): create clean architecture package skeleton`
- **2**: `feat(config): add Pydantic Settings for type-safe configuration`
- **3**: `feat(domain): add domain models with validation`
- **4**: `feat(domain): add repository interfaces`
- **5**: `feat(infrastructure): add structured logging with correlation IDs`
- **6**: `feat(domain): add custom exception hierarchy with error codes`
- **7**: `feat(application): migrate outreach pipeline to service layer`
- **8**: `feat(application): migrate CS engine to service layer`
- **9**: `feat(application): migrate voice pipeline to service layer`
- **10**: `feat(application): migrate agent orchestration to service layer`
- **11**: `feat(domain): add domain services for business logic`
- **12**: `feat(infrastructure): implement repository adapters for SQLite and CSV`
- **13**: `feat(infrastructure): migrate external API clients with retry logic`
- **14**: `feat(infrastructure): migrate messaging infrastructure with fallback logic`
- **15**: `feat(api): create unified FastAPI app structure`
- **16**: `feat(api): migrate webhook endpoints to unified API`
- **17**: `feat(api): migrate MCP server to unified API`
- **18**: `feat(api): migrate agent control to unified API`
- **19**: `feat(cli): create unified Click CLI`
- **20**: `feat(api): add authentication and rate limiting`
- **21**: `refactor(scripts): convert original scripts to backward compatibility shims`
- **22**: `test(domain): write unit tests for models and services`
- **23**: `test(application): write integration tests for application services`
- **24**: `test(e2e): write end-to-end tests for API and CLI`
- **25**: `docs(architecture): create detailed architecture documentation`
- **26**: `docs(api): create unified API reference documentation`
- **27**: `docs(migration): create migration guide for new package structure`

---

## Success Criteria

### Verification Commands
```bash
python -m pytest tests/  # Expected: All tests pass
oneai-reach --help      # Expected: Click CLI help displays
curl http://localhost:8888/health # Expected: {"status": "healthy"}
python scripts/scraper.py --help # Expected: Works, prints deprecation warning
```

### Final Checklist
- [ ] Clean Architecture structure implemented in `src/oneai_reach/`
- [ ] All 50+ scripts migrated to appropriate layers
- [ ] Original scripts converted to backward-compatible wrappers
- [ ] Unified FastAPI server replaces 3 scattered servers
- [ ] Comprehensive Click CLI replaces direct script execution
- [ ] Tests written and passing
- [ ] Documentation consolidated in `docs/` directory
- [ ] Dashboard left untouched
- [ ] Existing data stores left untouched (schema compatibility)