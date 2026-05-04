# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-27 23:47:04
**Commit:** 85a6b9c
**Branch:** master

## OVERVIEW
`1ai-reach` is a full cold outreach automation pipeline for BerkahKarya. It scrapes, enriches, generates AI proposals, sends them via multiple channels (email/WhatsApp), and tracks the entire funnel. The backend is Python with a Clean Architecture, and the frontend is a Next.js dashboard.

## STRUCTURE
```
./
├── src/                  # Main Python application source
│   └── oneai_reach/
│       ├── domain/       # Core business logic, models, and interfaces (pure)
│       ├── application/  # Use cases and service orchestration
│       ├── infrastructure/# External integrations (DB, APIs, LLMs)
│       ├── api/          # FastAPI endpoints and webhooks
│       └── cli/          # Click command-line interface
├── dashboard/            # Next.js frontend application
├── scripts/              # Legacy Python scripts (now shims to the new CLI)
├── data/                 # Lead data, proposals, templates, research outputs
│   ├── proposals/drafts/ # Generated proposal files
│   └── templates/        # Service proposal templates
├── tests/                # Pytest tests (unit, integration, e2e)
├── docs/                 # Documentation and guides
├── pyproject.toml        # Project configuration and dependencies
└── CLAUDE.md             # Detailed instructions for AI agents
```

## WHERE TO LOOK
| Task                                    | Location                             | Notes                                                 |
|-----------------------------------------|--------------------------------------|-------------------------------------------------------|
| Core business logic & models            | `src/oneai_reach/domain/`            | No external dependencies here. Pure Python.           |
| Implementing a new feature/use case     | `src/oneai_reach/application/`       | Orchestrates domain logic and infrastructure.         |
| Adding a new API (e.g., a new database) | `src/oneai_reach/infrastructure/`    | All external services, clients, and repos live here.  |
| Exposing a new HTTP endpoint            | `src/oneai_reach/api/`               | FastAPI routers and Pydantic models for the web layer.|
| Creating a new CLI command              | `src/oneai_reach/cli/`               | Uses Click to define commands.                        |
| Modifying the frontend UI               | `dashboard/`                         | A separate Next.js project.                           |
| Understanding the overall pipeline flow | `scripts/orchestrator.py`            | Legacy entry point, shows the high-level sequence.    |
| Checking hub integrations (WAHA, n8n)   | `scripts/config.py`                  | Contains all hub-related URLs and keys.               |

## CONVENTIONS
- **Clean Architecture**: Dependencies flow inwards: `api` -> `application` -> `domain`. `infrastructure` is also a detail. The `domain` layer must remain pure.
- **Dependency Injection**: Services are loosely coupled and dependencies are injected.
- **Repository Pattern**: Data access is abstracted via interfaces defined in `domain/repositories`. Implementations are in `infrastructure/database`.
- **Configuration**: All configuration is managed in `src/oneai_reach/config/settings.py` using Pydantic Settings. Do not hardcode values.
- **Path Management**: All paths should be absolute and sourced from `config.py`.
- **`displayName` Parsing**: Always use `parse_display_name()` from `utils.py` to handle the stringified dict format.

## ANTI-PATTERNS (THIS PROJECT)
- **DO NOT** hardcode paths, API keys, or any configuration. Use `config.py`.
- **DO NOT** add external library dependencies to the `domain` layer.
- **DO NOT** call `scripts` modules directly from `src`. A legacy bridge exists in `src/oneai_reach/infrastructure/legacy/` for controlled access.
- **DO NOT** manually construct paths like `"1ai-reach/..."`. Use the config.

## COMMANDS
```bash
# Run the full pipeline
python3 1ai-reach/scripts/orchestrator.py "Digital Agency in Jakarta"

# Run a dry run (no sending)
python3 1ai-reach/scripts/orchestrator.py "Coffee Shop in Jakarta" --dry-run

# Run only the follow-up cycle
python3 1ai-reach/scripts/orchestrator.py --followup-only

# Run tests
pytest
```

## NOTES
- **Hub Integration**: The project is tightly coupled with `berkahkarya-hub` for Brain API, WAHA, PaperClip, and n8n services. Config is in `config.py`.
- **LLM Chain**: The default LLM chain is Claude `sonnet` -> `gemini` -> `oracle`.
- **Legacy Scripts**: The `scripts/` directory contains the old structure. These are being phased out in favor of the new CLI in `src/oneai_reach/cli/`.
