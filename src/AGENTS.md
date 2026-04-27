# src - Main Application Source

This directory contains the core Python source code for the `1ai-reach` application, following Clean Architecture principles.

## STRUCTURE
```
src/
└── oneai_reach/
    ├── domain/       # Core business logic, models, and interfaces (pure)
    ├── application/  # Use cases and service orchestration
    ├── infrastructure/# External integrations (DB, APIs, LLMs)
    ├── api/          # FastAPI endpoints and webhooks
    └── cli/          # Click command-line interface
```

## WHERE TO LOOK
| Task                                | Location                | Notes                                          |
|-------------------------------------|-------------------------|------------------------------------------------|
| Adding a new business rule          | `oneai_reach/domain/`   | Should have no external library dependencies.  |
| Orchestrating a multi-step process  | `oneai_reach/application/`| Connects domain logic to infrastructure.       |
| Integrating a new third-party API   | `oneai_reach/infrastructure/`| Houses all external communication.             |
| Creating a new web endpoint         | `oneai_reach/api/`      | Defines public-facing contracts (Pydantic).    |

## CONVENTIONS
- **Dependency Rule**: Code in `src/` must only import from other modules within `src/` or from `pyproject.toml` dependencies.
- **Legacy Access**: The ONLY exception to the dependency rule is the legacy bridge at `src/oneai_reach/infrastructure/legacy/`, which provides controlled access to the older `scripts/` modules. Do not add new imports to this bridge.
