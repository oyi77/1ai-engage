# 1ai-reach Architecture

## Overview

1ai-reach follows **Clean Architecture** principles with clear separation of concerns across five layers.

## Architecture Layers

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

### 1. Domain Layer (`src/oneai_reach/domain/`)

**Pure business logic with zero external dependencies.**

- **Models**: Pydantic models (Lead, Conversation, Message, Proposal, KnowledgeEntry)
- **Services**: Business rules (LeadScoringService, ProposalValidator, FunnelCalculator)
- **Repositories**: Abstract interfaces (LeadRepository, ConversationRepository)
- **Exceptions**: Custom exceptions with error codes

**Key principle**: Domain layer knows nothing about databases, APIs, or frameworks.

### 2. Application Layer (`src/oneai_reach/application/`)

**Orchestrates domain services and coordinates workflows.**

- **Outreach**: Pipeline services (scraper, enricher, researcher, generator, reviewer, blaster)
- **Customer Service**: CS engine, conversation tracking, analytics, self-improvement
- **Voice**: STT, TTS, audio conversion, voice pipeline orchestration
- **Agents**: Strategy, closer, warmcall, autonomous loop

**Key principle**: Application services receive dependencies via constructor (dependency injection).

### 3. Infrastructure Layer (`src/oneai_reach/infrastructure/`)

**Implements external integrations and data persistence.**

- **Database**: SQLite repository adapters implementing domain repository interfaces
- **External**: API clients (BrainClient, WAHAClient, LLMClient)
- **Messaging**: Email and WhatsApp senders with fallback chains
- **Logging**: Structured JSON logging with correlation IDs

**Key principle**: Infrastructure adapts external systems to domain interfaces.

### 4. API Layer (`src/oneai_reach/api/`)

**Unified FastAPI application consolidating 3 previous servers.**

- **Webhooks**: WAHA (WhatsApp), CAPI (Meta Conversions API)
- **Admin**: Conversation management, pause/resume controls
- **Agents**: 30+ agent control endpoints
- **MCP**: JSON-RPC endpoint for AI agent control
- **Middleware**: Authentication (API key), rate limiting (100 req/min), CORS, logging

**Key principle**: API layer is thin - delegates to application services.

### 5. CLI Layer (`src/oneai_reach/cli/`)

**Click-based command-line interface with 7 command groups.**

- **funnel**: Manage leads and pipeline
- **stages**: Execute pipeline stages
- **jobs**: Background job management
- **wa**: WhatsApp session management
- **test**: Send test messages
- **system**: System status and configuration
- **kb**: Knowledge base management

**Key principle**: CLI delegates to same application services as API.

## Request Flow

```
HTTP Request → FastAPI Router
    ↓
Middleware (Auth, Rate Limit, Correlation ID)
    ↓
Route Handler (thin)
    ↓
Application Service (orchestration)
    ↓
Domain Service (business logic) + Repository (data access)
    ↓
Infrastructure (SQLite, External APIs)
```

## Key Design Patterns

### Dependency Injection

Services receive dependencies via constructor:

```python
class ScraperService:
    def __init__(self, settings: Settings):
        self.settings = settings
```

### Repository Pattern

Abstract data access behind interfaces:

```python
class LeadRepository(ABC):
    @abstractmethod
    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        pass
```

### Pydantic Settings

Type-safe configuration from environment variables:

```python
class Settings(BaseSettings):
    database: DatabaseSettings
    waha: WAHASettings
    # ... 14 configuration groups
```

### Structured Logging

JSON logs with correlation IDs for request tracing:

```python
logger = get_logger(__name__)
with correlation_id_context(request_id):
    logger.info("Processing request")
```

### Custom Exceptions

Domain-specific exceptions with error codes:

```python
raise LeadNotFoundError(lead_id="123")  # Error code: LEAD_001
```

## Configuration Management

**Single source of truth**: `src/oneai_reach/config/settings.py`

- 14 configuration groups (Database, Pipeline, LLM, Email, WAHA, etc.)
- Environment variable validation with Pydantic
- Singleton pattern with `@lru_cache`
- Type safety and IDE autocomplete

## Logging Strategy

**Structured JSON logging** for machine parsing:

- Dual output: console (colored) + file (JSON)
- Correlation IDs for request tracing
- Rotating file handler (10MB, 10 backups)
- Per-logger isolation (no propagation)

## Authentication & Security

- **API Key Authentication**: X-API-Key header
- **Dev Mode**: No keys configured = allow all (development)
- **Rate Limiting**: 100 requests/minute per IP (sliding window)
- **Secured Endpoints**: Admin, agents, MCP
- **Open Endpoints**: Webhooks, health checks

## Testing Strategy

- **Unit Tests**: 166 tests for domain layer (pure business logic)
- **Integration Tests**: 19 tests for application layer (mocked external deps)
- **E2E Tests**: 51 tests for API/CLI (46 passing, 5 known issues)
- **Coverage**: >80% of domain layer, >70% of application layer

## Backward Compatibility

**33 backward compatibility shims** maintain old script interfaces:

- Original scripts in `scripts/` now delegate to new CLI
- Deprecation warnings guide users to new commands
- Zero breaking changes for existing workflows
- Systemd services updated to use new CLI

## Directory Structure

```
src/oneai_reach/
├── domain/              # Business logic (pure)
│   ├── models/          # Pydantic models
│   ├── services/        # Business rules
│   ├── repositories/    # Abstract interfaces
│   └── exceptions.py    # Custom exceptions
├── application/         # Use cases & orchestration
│   ├── outreach/        # Pipeline services
│   ├── customer_service/# CS engine
│   ├── voice/           # Voice pipeline
│   └── agents/          # Agent orchestration
├── infrastructure/      # External integrations
│   ├── database/        # SQLite adapters
│   ├── external/        # API clients
│   ├── llm/             # LLM integration
│   ├── messaging/       # Email/WhatsApp
│   └── logging/         # Structured logs
├── api/                 # HTTP interface
│   ├── v1/              # API endpoints
│   ├── webhooks/        # Webhook handlers
│   ├── middleware.py    # Auth, rate limit
│   └── main.py          # FastAPI app
├── cli/                 # CLI interface
│   └── main.py          # Click commands
└── config/              # Configuration
    └── settings.py      # Pydantic Settings
```

## Benefits of This Architecture

1. **Testability**: Pure domain logic easy to test without mocks
2. **Maintainability**: Clear boundaries between layers
3. **Flexibility**: Easy to swap implementations (e.g., different database)
4. **Scalability**: Services can be extracted to microservices if needed
5. **Developer Experience**: Type safety, IDE autocomplete, clear structure

## Migration from Old Structure

See [migration_guide.md](migration_guide.md) for detailed migration instructions.

## API Reference

See [api_reference.md](api_reference.md) for complete API documentation.

## Data Models

See [data_models.md](data_models.md) for domain model reference.
