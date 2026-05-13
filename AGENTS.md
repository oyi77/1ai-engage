<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-05-06 | Updated: 2026-05-06 -->

# 1ai-reach

## Purpose
Communication and outreach automation platform with Python/FastAPI backend and Next.js 15 dashboard. Manages the full cold outreach pipeline: lead scraping → enrichment → AI proposal generation → multi-channel blasting (email/WhatsApp/SMS) → delivery tracking → customer service → self-improvement. Clean Architecture with domain/application/infrastructure layering and 54 legacy orchestration scripts.

## Key Files
| File | Description |
|------|-------------|
| `pyproject.toml` | Python dependencies, project metadata, entry points (api, cli, mcp) |
| `README.md` | Project overview and quick start guide |
| `.env.example` | Environment variable template |
| `uv.lock` | UV package manager lock file |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `src/` | Python package `oneai_reach` — Clean Architecture backend (see `src/AGENTS.md`) |
| `scripts/` | 54 core orchestration modules — legacy pipeline engine (see `scripts/AGENTS.md`) |
| `dashboard/` | Next.js 15 + React 19 frontend dashboard (see `dashboard/AGENTS.md`) |
| `data/` | SQLite databases, JSON knowledge bases, compliance data |
| `docs/` | Architecture docs, API reference, runbooks (17 files) |
| `tests/` | Pytest unit + integration + Playwright e2e tests |
| `systemd/` | 5 background service definitions (api, mcp, autonomous, dashboard, watchdog) |
| `assets/` | Static files (logo SVG) |
| `logs/` | Application log files |

## For AI Agents

### Working In This Directory
- Uses `uv` package manager — check `uv.lock` for dependency versions
- Clean Architecture: `domain/ → application/ → infrastructure/ → api/`
- Backend entry points defined in `pyproject.toml` scripts section
- API runs on port 8000, Dashboard on port 8502
- 5 systemd services for background processes
- Scripts/ directory contains legacy orchestration code — still active and in use
- Database: SQLite (raw `sqlite3`, no ORM) for performance
- MCP server available via `engage-mcp` entry point
- `scripts/brain_client.py` connects to `1ai-hub/` for shared memory

### Testing Requirements
- Backend: `python -m pytest tests/ -v`
- Dashboard e2e: `cd dashboard && npx playwright test`
- CI: GitHub Actions runs pytest on push
- Tests use isolated databases — never touch production data

### Common Patterns
- FastAPI v1 routes in `src/oneai_reach/api/v1/` — 32 endpoint modules
- Pydantic 2.0 schemas for request/response validation
- Application layer coordinates domain services
- Scripts use `sqlite3` directly for state persistence
- Knowledge bases stored as JSON in `data/`
- Multi-channel: email (SMTP), WhatsApp (WAHA), SMS
- Lead pipeline: scrape → enrich → generate → blast → track → follow up

## Dependencies

### Internal
- `scripts/brain_client.py` → `1ai-hub/` (shared memory/brain)
- `scripts/wa_manager.py` → `waha/` (WhatsApp API)

### External
- Python 3.10+ with FastAPI 0.104+, Uvicorn, Pydantic 2.0+
- Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui
- SWR (server state), React Hook Form + Zod
- SQLite (raw sqlite3, no ORM)
- Pandas, BeautifulSoup4 (data processing)
- WeasyPrint (PDF generation)
- Playwright (e2e testing)
- MCP 1.6+ (Model Context Protocol)

<!-- MANUAL: Custom project notes can be added below -->