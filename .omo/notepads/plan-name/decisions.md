
## Task 12: Repository Architecture Decisions (2026-04-17)

### Email Validation Strategy
**Decision**: Sanitize invalid emails at repository layer, not domain layer
**Rationale**: 
- Existing data contains malformed emails (`pt.@`, `%20` encoding)
- Domain models should remain strict (Pydantic EmailStr validation)
- Repository adapters handle dirty data → clean domain models

### Error Handling Pattern
**Decision**: Wrap all database errors in domain exceptions
**Pattern**:
```python
try:
    # DB operation
except sqlite3.Error as e:
    raise RepositoryError(f"Context: {e}")
```
**Rationale**: Isolates infrastructure concerns from domain logic

### Connection Management
**Decision**: Create new connection per operation, no connection pooling
**Rationale**:
- SQLite WAL mode handles concurrency
- `check_same_thread=False` allows multi-threaded access
- Simpler than managing connection pool lifecycle

### CSV Backward Compatibility
**Decision**: Maintain separate CSVLeadRepository implementation
**Rationale**:
- Existing scripts depend on CSV format
- Gradual migration path (CSV → SQLite)
- Both implementations share same interface

## Task 13: External API Clients Architecture (2026-04-17)

### Retry Logic
- **Decision**: Use decorator pattern for retry logic
- **Rationale**: Clean separation of concerns, reusable across all clients
- **Implementation**: 3 retries with exponential backoff (1s, 2s, 4s)

### Rate Limiting
- **Decision**: Per-client rate limiters with sliding window
- **Rationale**: Prevents API quota exhaustion, different limits per service
- **Implementation**: Timestamp-based tracking, raises APIRateLimitError with wait time

### Error Handling Strategy
- **Decision**: BrainClient fails silently, others raise exceptions
- **Rationale**: Brain is optional (learning system), WAHA/n8n are critical
- **Implementation**: Try-except with domain exception wrapping

### LLM Fallback Chain
- **Decision**: Cascade through 8 providers (aitradepulse → opencode → ollama → claude CLI → anthropic API → gemini API → groq → openai)
- **Rationale**: Maximum availability, graceful degradation
- **Implementation**: Sequential try-return pattern with optional fallback message

### Settings Injection
- **Decision**: Constructor-based dependency injection
- **Rationale**: Testability, no global state, explicit dependencies
- **Implementation**: All clients accept Settings object in __init__

### WAHA URL Resolution
- **Decision**: Prefer primary URL/key, fallback to direct
- **Rationale**: Supports multiple WAHA instances (proxy vs direct)
- **Implementation**: _resolve_url() and _resolve_api_key() methods


## Task 13: External API Clients Architecture (2025-04-17)

### Retry Logic
- **Decision**: Use decorator pattern for retry logic
- **Rationale**: Clean separation of concerns, reusable across all clients
- **Implementation**: 3 retries with exponential backoff (1s, 2s, 4s)

### Rate Limiting
- **Decision**: Per-client rate limiters with sliding window
- **Rationale**: Prevents API quota exhaustion, different limits per service
- **Implementation**: Timestamp-based tracking, raises APIRateLimitError with wait time

### Error Handling Strategy
- **Decision**: BrainClient fails silently, others raise exceptions
- **Rationale**: Brain is optional (learning system), WAHA/n8n are critical
- **Implementation**: Try-except with domain exception wrapping

### LLM Fallback Chain
- **Decision**: Cascade through 8 providers (aitradepulse → opencode → ollama → claude CLI → anthropic API → gemini API → groq → openai)
- **Rationale**: Maximum availability, graceful degradation
- **Implementation**: Sequential try-return pattern with optional fallback message

### Settings Injection
- **Decision**: Constructor-based dependency injection
- **Rationale**: Testability, no global state, explicit dependencies
- **Implementation**: All clients accept Settings object in __init__

### WAHA URL Resolution
- **Decision**: Prefer primary URL/key, fallback to direct
- **Rationale**: Supports multiple WAHA instances (proxy vs direct)
- **Implementation**: _resolve_url() and _resolve_api_key() methods

