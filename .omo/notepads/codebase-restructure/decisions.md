
## Task 7 Part 1: Service Layer Architecture (2026-04-17)

### Decision: Service Layer Pattern
**Context**: Need to extract business logic from scripts into reusable, testable services.

**Decision**: Created application service layer with dependency injection pattern:
- Services receive Settings via constructor (not repositories yet - deferred to Task 12)
- Services return dict instead of domain models (Lead conversion deferred to Task 12)
- Services remain synchronous (async refactoring deferred to Wave 3)

**Rationale**:
- Incremental migration reduces risk
- Services can be tested independently
- Original scripts remain backward compatible
- Clear separation of concerns (business logic vs CLI)

### Decision: Keep External Clients As-Is
**Context**: Services use subprocess for AgentCash, requests for HTTP calls.

**Decision**: Keep external API clients embedded in services for now.

**Rationale**:
- External client abstraction is Task 13 scope
- Avoid scope creep in this task
- Services are already testable with mocking
- Can refactor to injected clients later without breaking consumers

### Decision: Preserve Original Script Behavior
**Context**: Scripts are used by orchestrator and manual CLI invocation.

**Decision**: Keep scripts as thin wrappers that instantiate services and delegate.

**Rationale**:
- Backward compatibility critical for existing workflows
- Scripts remain entry points for CLI usage
- Service layer provides reusability for future consumers (API, tests, etc.)


## Task 9: Voice Pipeline Services Architecture (2026-04-17)

### Decision: Keep ML Model Lazy-Loading Pattern
**Rationale**: Voice models (faster-whisper, ChatterBox) are large and slow to load. Lazy-loading on first use prevents startup delays and allows services to be imported without triggering model downloads.

### Decision: Use Subprocess for Audio Conversion
**Rationale**: ffmpeg subprocess is lightweight and avoids heavy Python audio libraries. Keeps dependencies minimal and leverages battle-tested system tools.

### Decision: Maintain Singleton Pattern for Engines
**Rationale**: ML models should be loaded once and reused across requests. Singleton pattern via `get_stt_service()` and `get_tts_service()` ensures single model instance per process.

### Decision: Preserve Original Scripts as Thin Wrappers
**Rationale**: Existing code (cs_engine, webhook handlers) imports from `scripts/`. Thin wrappers maintain backward compatibility while delegating to new services. Zero migration effort for existing callers.

### Decision: Integrate with Existing state_manager for Config
**Rationale**: Voice config is per-session (stored in DB via `state_manager`). Services call existing `get_voice_config(session_name)` to maintain consistency with current system.

### Decision: Use sys.path Injection for Cross-Module Access
**Rationale**: Services need to call `cs_engine` and `senders` from scripts/. Temporary sys.path injection allows access without circular dependencies or major refactoring.


## Task 10: Agent Service Architecture (2026-04-17)

### Decision: Service Method Signatures
**Context**: Original scripts used inconsistent parameter names (wa_number_id vs session, contact_phone vs phone)

**Decision**: Standardize to shorter, clearer names:
- `phone` instead of `contact_phone`
- `name` instead of `contact_name`
- `session` instead of `wa_number_id`

**Rationale**:
- Consistency across all agent services
- Shorter parameter names improve readability
- Matches domain language (users say "phone" not "contact_phone")

**Trade-offs**:
- Requires updating callers to use new parameter names
- Breaking change for direct script imports (mitigated by backward compatibility layer)

---

### Decision: WarmcallService Complexity
**Context**: warmcall_engine.py is 900 lines with complex state management

**Decision**: Keep service at 680 lines, extract all logic into service methods

**Rationale**:
- Single responsibility: warmcall orchestration
- All related logic (intent classification, follow-up scheduling, message generation) belongs together
- Splitting would create artificial boundaries and increase coupling

**Trade-offs**:
- Large service class (680 lines)
- Could be split into WarmcallOrchestrator + WarmcallMessageGenerator in future
- Acceptable for now given cohesion of functionality

---

### Decision: AutonomousService State Management
**Context**: autonomous_loop.py tracks running subprocesses in global dict

**Decision**: Move `_running` dict to instance variable

**Rationale**:
- Enables multiple autonomous service instances (testing, multi-tenant)
- Cleaner dependency injection
- Easier to mock in tests

**Trade-offs**:
- Instance state makes service stateful (not pure)
- Acceptable for orchestration service that manages long-running processes


## Task 16: Webhook Migration Architecture Decisions (2026-04-17)

### Decision: Direct Import vs Dependency Injection
**Choice**: Used direct imports from scripts/ directory instead of DI
**Rationale**: 
- Original functions (handle_inbound_message, get_wa_number_by_session) are stateless
- No need for complex DI setup when simple imports work
- Preserves exact behavior of original Flask implementation
- Easier to maintain during transition period

### Decision: Keep webhook_server.py as Wrapper
**Choice**: Added deprecation notice but kept Flask server intact
**Rationale**:
- Allows gradual migration for external systems
- Provides clear migration path in deprecation notice
- No breaking changes for existing integrations
- Can be removed after full migration confirmed

### Decision: 404 for Missing Session is Correct
**Choice**: Preserve original behavior of returning 404 when session not found
**Rationale**:
- Original Flask implementation returns 404 for unknown sessions
- This is correct behavior - webhook should fail fast if session doesn't exist
- External systems expect this behavior
- Test showing 404 confirms correct implementation, not a bug

### Decision: Global _processed_messages Set
**Choice**: Keep module-level set for duplicate detection
**Rationale**:
- Matches original Flask implementation exactly
- Simple and effective for duplicate detection
- Auto-clears after 1000 messages to prevent memory growth
- No need for Redis/external cache at this scale


## Task 17: MCP Migration Architecture Decisions (2026-04-18)

### Decision: JSON-RPC 2.0 Protocol
- **Rationale**: MCP protocol uses JSON-RPC 2.0 for method invocation
- **Implementation**: Single POST endpoint at `/api/v1/mcp/` handles all methods
- **Benefits**: Standard protocol, easy to test, client-agnostic

### Decision: Unified Handler Signature
- **Problem**: Original handlers had inconsistent signatures (some took params, some didn't)
- **Solution**: All handlers accept `params: Dict[str, Any] = None` with null guards
- **Benefits**: Consistent invocation logic, no special cases, easier to maintain

### Decision: Method Registry Pattern
- **Rationale**: Centralized mapping of method names to handler functions
- **Implementation**: `MCP_METHODS` dict with 34 entries
- **Benefits**: Easy to add new methods, clear method inventory, supports discovery endpoint

### Decision: Keep mcp_server.py as Wrapper
- **Rationale**: Existing clients may depend on FastMCP interface
- **Implementation**: Added deprecation notice, kept original functionality
- **Benefits**: Backward compatibility, gradual migration path

### Decision: No Dependency Injection for MCP
- **Rationale**: MCP handlers call agent_control module directly (existing pattern)
- **Implementation**: Import agent_control at module level, call functions directly
- **Benefits**: Simpler implementation, matches existing codebase patterns

