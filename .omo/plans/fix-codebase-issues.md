# Fix 1ai-reach Codebase Issues

## TL;DR

> **Quick Summary**: Fix 9 issues found in comprehensive codebase audit: 1 critical (API service down), 5 high priority (dependencies, error handling, imports, logging), 3 medium priority (package name, build artifacts, refactoring).
> 
> **Deliverables**:
> - API service restored and running
> - Dashboard dependencies installed
> - Proper error handling (no bare except clauses)
> - Clean import system (package-based, no sys.path hacks)
> - Professional logging (replace print statements)
> - Clean repository (no build artifacts)
> - Correct package name
> 
> **Estimated Effort**: Medium (5-6 hours total)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 2 → Verification

---

## Context

### Original Request
User requested comprehensive codebase analysis and planning to fix all issues found in the 1ai-reach project.

### Audit Summary
**Conducted**: 2026-04-20 using 4 parallel background agents + direct analysis
**Scope**: 50,000+ lines of code, all services, dependencies, security
**Findings**: 9 issues across 3 severity levels
**Security Status**: ✅ PASSED (no vulnerabilities)

**Audit Reports Generated**:
- `AUDIT_REPORT.md` - Complete findings (7.3K)
- `FIX_PROPOSALS.md` - Step-by-step solutions (6.7K)
- `QUICK_FIX_GUIDE.md` - Emergency procedures (3.9K)
- `AUDIT_INDEX.md` - Navigation guide

### Metis Review
**Key Findings from Metis**:
- Rollback strategy needed (API is down)
- Test strategy required (verify fixes don't break functionality)
- Scope boundaries must be explicit (prevent scope creep)
- Commit strategy should be atomic (one fix per commit)
- Documentation updates needed after fixes

**Guardrails Applied**:
- NO feature additions (fixes only)
- NO refactoring beyond what's necessary
- NO changes to business logic
- NO modifications to database schema
- Test after EVERY fix before proceeding

---

## Work Objectives

### Core Objective
Restore API service to working state and eliminate all technical debt identified in the audit, improving code quality, maintainability, and reliability without changing any business logic or features.

### Concrete Deliverables
- API service running without errors (systemd status = active)
- Dashboard building and running successfully
- Zero bare except clauses in codebase
- Package installed in editable mode (no sys.path manipulation)
- All print() replaced with proper logging
- Build artifacts removed from repository
- Package name corrected in pyproject.toml
- All services verified working end-to-end

### Definition of Done
- [ ] `systemctl status 1ai-reach-api.service` shows "active (running)"
- [ ] `curl http://localhost:8000/health` returns 200 OK
- [ ] `systemctl status 1ai-reach-dashboard.service` shows "active (running)"
- [ ] Dashboard loads at http://localhost:8502
- [ ] No bare `except:` clauses in src/oneai_reach/application/voice/
- [ ] `pip show oneai-reach` shows package installed
- [ ] No sys.path.insert() in scripts/ directory
- [ ] No print() statements in webhook_server.py or mcp_server.py
- [ ] `git status` shows no __pycache__ or .pyc files
- [ ] Package name is "oneai-reach" in pyproject.toml

### Must Have
- API service restored (CRITICAL)
- Dashboard dependencies installed
- Specific exception types (no bare except)
- Proper logging infrastructure
- Clean git repository

### Must NOT Have (Guardrails)
- NO new features or functionality
- NO changes to business logic
- NO database schema modifications
- NO API endpoint changes
- NO breaking changes to existing interfaces
- NO refactoring beyond fixing identified issues
- NO "while we're at it" improvements
- NO premature optimization

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, systemd services)
- **Automated tests**: Tests-after (verify fixes don't break functionality)
- **Framework**: pytest + systemd + curl
- **Test Strategy**: Integration tests after each phase

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Services**: Use Bash (systemctl, curl) — Check status, test endpoints
- **Python Code**: Use Bash (python -c) — Import modules, run syntax checks
- **Dashboard**: Use Bash (npm, curl) — Build, start, test loading
- **Files**: Use Bash (grep, find) — Verify changes applied correctly

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.

```
Wave 1 (CRITICAL - Start Immediately):
├── Task 1: Fix API import error [quick] ⚠️ BLOCKING
└── Task 2: Install dashboard dependencies [quick]

Wave 2 (HIGH PRIORITY - After Wave 1):
├── Task 3: Fix bare except clauses [quick]
├── Task 4: Install package in editable mode [quick]
├── Task 5: Remove sys.path from orchestrator.py [quick]
└── Task 6: Remove sys.path from enricher.py [quick]

Wave 3 (HIGH PRIORITY CONTINUED):
├── Task 7: Replace print() in webhook_server.py [quick]
├── Task 8: Replace print() in mcp_server.py [quick]
├── Task 9: Clean old workspace paths [quick]
└── Task 10: Fix package name [quick]

Wave 4 (MEDIUM PRIORITY):
├── Task 11: Clean build artifacts [quick]
├── Task 12: Update .gitignore [quick]
└── Task 13: Verify all services [unspecified-high]

Wave FINAL (VERIFICATION):
└── Task 14: End-to-end integration test [unspecified-high]
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|------------|--------|------|
| 1 | — | 2, 13, 14 | 1 |
| 2 | — | 13, 14 | 1 |
| 3 | 1 | 14 | 2 |
| 4 | 1 | 5, 6, 14 | 2 |
| 5 | 4 | 14 | 2 |
| 6 | 4 | 14 | 2 |
| 7 | 1 | 14 | 3 |
| 8 | 1 | 14 | 3 |
| 9 | 2 | 14 | 3 |
| 10 | 1 | 14 | 3 |
| 11 | — | 12 | 4 |
| 12 | 11 | 14 | 4 |
| 13 | 1, 2 | 14 | 4 |
| 14 | ALL | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: 2 tasks → `quick` (critical fixes)
- **Wave 2**: 4 tasks → `quick` (parallel cleanup)
- **Wave 3**: 4 tasks → `quick` (parallel improvements)
- **Wave 4**: 3 tasks → `quick` + `unspecified-high` (verification)
- **Wave FINAL**: 1 task → `unspecified-high` (integration test)

---

## TODOs

- [ ] 1. Fix API Import Error (CRITICAL)

  **What to do**:
  - Backup the broken file: `cp src/oneai_reach/api/v1/legacy.py src/oneai_reach/api/v1/legacy.py.backup`
  - Change line 14 from `from voice_config import get_voice_config, update_voice_config` to two separate imports:
    - `from voice_config import get_voice_config`
    - `from state_manager import update_voice_config`
  - Restart API service: `sudo systemctl restart 1ai-reach-api.service`
  - Verify service is running

  **Must NOT do**:
  - Do NOT modify any other imports
  - Do NOT change function signatures
  - Do NOT add new functionality

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple import fix, single file, clear solution
  - **Skills**: []
    - No special skills needed for basic import fix

  **Parallelization**:
  - **Can Run In Parallel**: NO (blocks everything else)
  - **Parallel Group**: Wave 1 (critical)
  - **Blocks**: Tasks 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14
  - **Blocked By**: None (start immediately)

  **References**:
  
  **Current Code** (src/oneai_reach/api/v1/legacy.py:14):
  - Line 14: `from voice_config import get_voice_config, update_voice_config`
  
  **Function Location**:
  - `update_voice_config` exists in: `scripts/state_manager.py:581`
  - `get_voice_config` exists in: `scripts/voice_config.py:96`
  
  **Error Evidence**:
  - `journalctl -u 1ai-reach-api.service` shows: `ImportError: cannot import name 'update_voice_config' from 'voice_config'`
  
  **Fix Pattern**:
  - AUDIT_REPORT.md:Critical Issue #1
  - FIX_PROPOSALS.md:Critical Fix #1
  - QUICK_FIX_GUIDE.md:5-Minute Emergency Fix

  **Acceptance Criteria**:
  
  - [ ] File backed up to src/oneai_reach/api/v1/legacy.py.backup
  - [ ] Line 14 split into two import statements
  - [ ] Service restarted: `sudo systemctl restart 1ai-reach-api.service`
  - [ ] Service status: `systemctl status 1ai-reach-api.service` shows "active (running)"
  - [ ] No ImportError in logs: `journalctl -u 1ai-reach-api.service -n 20 | grep ImportError` returns nothing

  **QA Scenarios**:

  ```
  Scenario: API service starts successfully after import fix
    Tool: Bash (systemctl + curl)
    Preconditions: Import error fixed in legacy.py
    Steps:
      1. Restart service: sudo systemctl restart 1ai-reach-api.service
      2. Wait 3 seconds: sleep 3
      3. Check status: systemctl status 1ai-reach-api.service --no-pager
      4. Verify active: systemctl is-active 1ai-reach-api.service
      5. Test health endpoint: curl -f http://localhost:8000/health
    Expected Result: Service shows "active (running)", health endpoint returns 200 OK
    Failure Indicators: Service shows "failed" or "activating", curl returns error
    Evidence: .sisyphus/evidence/task-1-api-service-start.log

  Scenario: Import error no longer appears in logs
    Tool: Bash (journalctl + grep)
    Preconditions: Service restarted after fix
    Steps:
      1. Get last 50 log lines: journalctl -u 1ai-reach-api.service -n 50 --no-pager
      2. Search for ImportError: grep -i "importerror" 
      3. Search for update_voice_config: grep "update_voice_config"
    Expected Result: No ImportError found, no mention of missing update_voice_config
    Failure Indicators: ImportError still present, service still crashing
    Evidence: .sisyphus/evidence/task-1-no-import-error.log
  ```

  **Evidence to Capture**:
  - [ ] Backup file exists: ls -la src/oneai_reach/api/v1/legacy.py.backup
  - [ ] Service status output saved
  - [ ] Health endpoint response saved
  - [ ] Log excerpt showing no errors

  **Commit**: YES
  - Message: `fix(api): correct import path for update_voice_config`
  - Files: `src/oneai_reach/api/v1/legacy.py`
  - Pre-commit: `python3 -m py_compile src/oneai_reach/api/v1/legacy.py && sudo systemctl restart 1ai-reach-api.service && sleep 3 && systemctl is-active 1ai-reach-api.service`

- [ ] 2. Install Dashboard Dependencies

  **What to do**:
  - Navigate to dashboard directory: `cd dashboard`
  - Install all npm dependencies: `npm install`
  - Verify Next.js binary exists: `ls -la node_modules/.bin/next`
  - Test build works: `npm run build`
  - Restart dashboard service: `sudo systemctl restart 1ai-reach-dashboard.service`

  **Must NOT do**:
  - Do NOT upgrade package versions beyond what's in package.json
  - Do NOT modify package.json
  - Do NOT change any dashboard code

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard npm install, no code changes
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1, but Task 1 is more critical)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 9, 13, 14
  - **Blocked By**: None

  **References**:
  
  **Missing Dependencies** (from npm list):
  - `@base-ui/react@^1.4.0`
  - `@playwright/test@^1.59.1`
  - `@tailwindcss/postcss@^4`
  - `@types/node@^20`
  - `@types/react-dom@^19`
  - `@types/react@^19`
  - `class-variance-authority@^0.7.1`
  - `clsx@^2.1.1`
  - `eslint-config-next@16.2.3`
  - `eslint@^9`
  
  **Current State**:
  - `dashboard/package-lock.json` exists
  - `npm run build` fails with "next: not found"
  
  **Fix Pattern**:
  - AUDIT_REPORT.md:Critical Issue #2
  - FIX_PROPOSALS.md:Critical Fix #2

  **Acceptance Criteria**:
  
  - [ ] `npm install` completes without errors
  - [ ] `npm list 2>&1 | grep UNMET` returns no results
  - [ ] `node_modules/.bin/next` exists and is executable
  - [ ] `npm run build` completes successfully
  - [ ] Dashboard service running: `systemctl is-active 1ai-reach-dashboard.service`

  **QA Scenarios**:

  ```
  Scenario: Dashboard builds successfully after dependency install
    Tool: Bash (npm)
    Preconditions: In dashboard/ directory
    Steps:
      1. Install dependencies: npm install
      2. Check for unmet deps: npm list 2>&1 | grep UNMET
      3. Verify next binary: test -x node_modules/.bin/next && echo "EXISTS"
      4. Build dashboard: npm run build
      5. Check build output: test -d .next && echo "BUILD_SUCCESS"
    Expected Result: npm install succeeds, no UNMET deps, build creates .next directory
    Failure Indicators: npm install fails, UNMET deps remain, build fails
    Evidence: .sisyphus/evidence/task-2-dashboard-build.log

  Scenario: Dashboard service starts and serves content
    Tool: Bash (systemctl + curl)
    Preconditions: Dependencies installed, build successful
    Steps:
      1. Restart service: sudo systemctl restart 1ai-reach-dashboard.service
      2. Wait 5 seconds: sleep 5
      3. Check status: systemctl is-active 1ai-reach-dashboard.service
      4. Test endpoint: curl -f http://localhost:8502
      5. Verify HTML: curl -s http://localhost:8502 | grep -q "<html"
    Expected Result: Service active, port 8502 returns HTML content
    Failure Indicators: Service failed, port not responding, no HTML
    Evidence: .sisyphus/evidence/task-2-dashboard-running.log
  ```

  **Evidence to Capture**:
  - [ ] npm install output
  - [ ] npm list showing no UNMET dependencies
  - [ ] Build success confirmation
  - [ ] Service status

  **Commit**: YES
  - Message: `build(dashboard): install missing npm dependencies`
  - Files: `dashboard/package-lock.json`
  - Pre-commit: `cd dashboard && npm run build && cd ..`

- [ ] 3. Fix Bare Except Clauses in Voice Modules

  **What to do**:
  - Fix 4 bare `except:` clauses to use specific exception types
  - File 1: `src/oneai_reach/application/voice/voice_pipeline_service.py:215` → `except Exception as e:`
  - File 2: `src/oneai_reach/application/voice/tts_service.py:170` → `except ImportError:`
  - File 3: `src/oneai_reach/application/voice/audio_service.py:176` → `except (ValueError, UnicodeDecodeError):`
  - File 4: `src/oneai_reach/application/voice/audio_service.py:301` → `except Exception as e:`
  - Add logging where appropriate

  **Must NOT do**:
  - Do NOT change the fallback logic
  - Do NOT modify function signatures
  - Do NOT add new dependencies

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple exception type changes, 4 files, clear pattern
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 5, 6)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 14
  - **Blocked By**: Task 1 (API must be working)

  **References**:
  
  **Location 1** (voice_pipeline_service.py:215):
  ```python
  # Current:
  except:
      pass
  
  # Fix to:
  except Exception as e:
      logger.warning(f"Failed to stop typing indicator: {e}")
  ```
  
  **Location 2** (tts_service.py:170):
  ```python
  # Current:
  except:
      sentences = [s.strip() for s in text.split(".") if s.strip()]
  
  # Fix to:
  except ImportError:
      # Fallback if nltk not available
      sentences = [s.strip() for s in text.split(".") if s.strip()]
  ```
  
  **Location 3** (audio_service.py:176):
  ```python
  # Current:
  except:
      sample_rate = 16000
  
  # Fix to:
  except (ValueError, UnicodeDecodeError):
      sample_rate = 16000  # Default fallback
  ```
  
  **Location 4** (audio_service.py:301):
  ```python
  # Current:
  except:
      # fallback
  
  # Fix to:
  except Exception as e:
      logger.warning(f"Audio conversion fallback: {e}")
      # fallback
  ```
  
  **Pattern Reference**:
  - AUDIT_REPORT.md:High Priority Issue #1
  - FIX_PROPOSALS.md:High Priority Fix #1

  **Acceptance Criteria**:
  
  - [ ] No bare `except:` in voice_pipeline_service.py
  - [ ] No bare `except:` in tts_service.py
  - [ ] No bare `except:` in audio_service.py
  - [ ] All 4 locations use specific exception types
  - [ ] Logging added where appropriate
  - [ ] Files compile: `python3 -m py_compile <file>`

  **QA Scenarios**:

  ```
  Scenario: No bare except clauses remain in voice modules
    Tool: Bash (grep)
    Preconditions: All 4 files modified
    Steps:
      1. Search voice_pipeline_service.py: grep -n "except:" src/oneai_reach/application/voice/voice_pipeline_service.py
      2. Search tts_service.py: grep -n "except:" src/oneai_reach/application/voice/tts_service.py
      3. Search audio_service.py: grep -n "except:" src/oneai_reach/application/voice/audio_service.py
      4. Count total: grep -r "except:" src/oneai_reach/application/voice/ | wc -l
    Expected Result: All greps return no results (exit code 1), count is 0
    Failure Indicators: Any bare except: found
    Evidence: .sisyphus/evidence/task-3-no-bare-except.log

  Scenario: Modified files compile without syntax errors
    Tool: Bash (python -m py_compile)
    Preconditions: All 4 files modified
    Steps:
      1. Compile voice_pipeline_service.py: python3 -m py_compile src/oneai_reach/application/voice/voice_pipeline_service.py
      2. Compile tts_service.py: python3 -m py_compile src/oneai_reach/application/voice/tts_service.py
      3. Compile audio_service.py: python3 -m py_compile src/oneai_reach/application/voice/audio_service.py
      4. Check for .pyc files: find src/oneai_reach/application/voice/__pycache__ -name "*.pyc" | wc -l
    Expected Result: All compile commands succeed (exit 0), .pyc files created
    Failure Indicators: SyntaxError, compilation fails
    Evidence: .sisyphus/evidence/task-3-compile-success.log
  ```

  **Evidence to Capture**:
  - [ ] Grep output showing no bare except
  - [ ] Compilation success for all files
  - [ ] Diff showing changes made

  **Commit**: YES
  - Message: `fix(voice): replace bare except with specific exceptions`
  - Files: `src/oneai_reach/application/voice/voice_pipeline_service.py`, `src/oneai_reach/application/voice/tts_service.py`, `src/oneai_reach/application/voice/audio_service.py`
  - Pre-commit: `python3 -m py_compile src/oneai_reach/application/voice/*.py`

- [ ] 4. Install Package in Editable Mode

  **What to do**:
  - Navigate to project root: `cd /home/openclaw/projects/1ai-reach`
  - Install package in editable mode: `pip install -e .`
  - Verify installation: `pip show oneai-reach`
  - Test imports work: `python3 -c "from oneai_reach.domain.models import Lead; print('OK')"`

  **Must NOT do**:
  - Do NOT modify pyproject.toml yet (Task 10 will fix package name)
  - Do NOT uninstall existing packages
  - Do NOT upgrade dependencies

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard pip install, no code changes
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 5, 6, 14
  - **Blocked By**: Task 1 (API must be working)

  **References**:
  
  **Current State**:
  - Package not installed in editable mode
  - 76 scripts use `sys.path.insert(0, str(_src))` to make imports work
  
  **Package Structure**:
  - `pyproject.toml` defines package as "oneai-engage" (will be fixed in Task 10)
  - Source code in `src/oneai_reach/`
  - Scripts in `scripts/`
  
  **Pattern Reference**:
  - AUDIT_REPORT.md:High Priority Issue #2
  - FIX_PROPOSALS.md:High Priority Fix #2

  **Acceptance Criteria**:
  
  - [ ] `pip install -e .` completes successfully
  - [ ] `pip show oneai-engage` shows package installed (name will be fixed in Task 10)
  - [ ] `python3 -c "from oneai_reach.domain.models import Lead"` works without sys.path manipulation
  - [ ] Package location shows editable install: `pip show oneai-engage | grep Location`

  **QA Scenarios**:

  ```
  Scenario: Package installs in editable mode successfully
    Tool: Bash (pip)
    Preconditions: In project root directory
    Steps:
      1. Install package: pip install -e .
      2. Check installation: pip show oneai-engage
      3. Verify editable: pip show oneai-engage | grep "Editable project location"
      4. List installed files: pip show -f oneai-engage | head -20
    Expected Result: Package installed, shows editable location, no errors
    Failure Indicators: pip install fails, package not found
    Evidence: .sisyphus/evidence/task-4-pip-install.log

  Scenario: Imports work without sys.path manipulation
    Tool: Bash (python -c)
    Preconditions: Package installed in editable mode
    Steps:
      1. Test domain import: python3 -c "from oneai_reach.domain.models import Lead; print('Lead OK')"
      2. Test application import: python3 -c "from oneai_reach.application.voice import VoicePipelineService; print('Voice OK')"
      3. Test infrastructure import: python3 -c "from oneai_reach.infrastructure.database import Database; print('DB OK')"
      4. Test API import: python3 -c "from oneai_reach.api.main import create_app; print('API OK')"
    Expected Result: All imports succeed, print OK messages
    Failure Indicators: ImportError, ModuleNotFoundError
    Evidence: .sisyphus/evidence/task-4-imports-work.log
  ```

  **Evidence to Capture**:
  - [ ] pip install output
  - [ ] pip show output
  - [ ] Import test results

  **Commit**: YES
  - Message: `build: install package in editable mode`
  - Files: None (pip install doesn't modify tracked files)
  - Pre-commit: `pip show oneai-engage && python3 -c "from oneai_reach.domain.models import Lead"`

- [ ] 5. Remove sys.path from orchestrator.py

  **What to do**:
  - Open `scripts/orchestrator.py`
  - Remove lines 21-22 (sys.path manipulation)
  - Verify script still runs: `python3 scripts/orchestrator.py --help`
  - Test imports work without sys.path

  **Must NOT do**:
  - Do NOT modify any other logic in the script
  - Do NOT change command-line arguments
  - Do NOT add new imports

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple deletion, single file
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 6)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 14
  - **Blocked By**: Task 4 (package must be installed)

  **References**:
  
  **Current Code** (scripts/orchestrator.py:21-22):
  ```python
  _src = Path(__file__).parent.parent / "src"
  sys.path.insert(0, str(_src))
  ```
  
  **After Task 4**: Package installed, imports work without sys.path
  
  **Pattern Reference**:
  - AUDIT_REPORT.md:High Priority Issue #2
  - FIX_PROPOSALS.md:High Priority Fix #2

  **Acceptance Criteria**:
  
  - [ ] Lines 21-22 removed from orchestrator.py
  - [ ] No `sys.path.insert` in orchestrator.py: `grep "sys.path.insert" scripts/orchestrator.py` returns nothing
  - [ ] Script runs: `python3 scripts/orchestrator.py --help` succeeds
  - [ ] Imports work: Script can import from oneai_reach package

  **QA Scenarios**:

  ```
  Scenario: orchestrator.py runs without sys.path manipulation
    Tool: Bash (python + grep)
    Preconditions: Package installed, sys.path lines removed
    Steps:
      1. Check no sys.path: grep "sys.path.insert" scripts/orchestrator.py
      2. Test help: python3 scripts/orchestrator.py --help
      3. Test dry-run: python3 scripts/orchestrator.py "test query" --dry-run
      4. Check imports: python3 -c "import sys; sys.path.insert(0, 'scripts'); import orchestrator; print('OK')"
    Expected Result: No sys.path found, help works, dry-run works, imports succeed
    Failure Indicators: sys.path still present, script fails, ImportError
    Evidence: .sisyphus/evidence/task-5-orchestrator-clean.log
  ```

  **Evidence to Capture**:
  - [ ] Grep showing no sys.path
  - [ ] Script help output
  - [ ] Dry-run success

  **Commit**: NO (groups with Task 6)

- [ ] 6. Remove sys.path from enricher.py

  **What to do**:
  - Open `scripts/enricher.py`
  - Remove lines 21-22 (sys.path manipulation)
  - Verify script still runs: `python3 scripts/enricher.py --help`
  - Test imports work without sys.path

  **Must NOT do**:
  - Do NOT modify any other logic in the script
  - Do NOT change enrichment logic
  - Do NOT add new imports

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple deletion, single file
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 14
  - **Blocked By**: Task 4 (package must be installed)

  **References**:
  
  **Current Code** (scripts/enricher.py:21-22):
  ```python
  _src = Path(__file__).parent.parent / "src"
  sys.path.insert(0, str(_src))
  ```
  
  **Pattern**: Same as Task 5
  
  **Pattern Reference**:
  - AUDIT_REPORT.md:High Priority Issue #2
  - FIX_PROPOSALS.md:High Priority Fix #2

  **Acceptance Criteria**:
  
  - [ ] Lines 21-22 removed from enricher.py
  - [ ] No `sys.path.insert` in enricher.py: `grep "sys.path.insert" scripts/enricher.py` returns nothing
  - [ ] Script runs: `python3 scripts/enricher.py --help` succeeds
  - [ ] Imports work: Script can import from oneai_reach package

  **QA Scenarios**:

  ```
  Scenario: enricher.py runs without sys.path manipulation
    Tool: Bash (python + grep)
    Preconditions: Package installed, sys.path lines removed
    Steps:
      1. Check no sys.path: grep "sys.path.insert" scripts/enricher.py
      2. Test script: python3 scripts/enricher.py --help
      3. Check imports: python3 -c "import sys; sys.path.insert(0, 'scripts'); import enricher; print('OK')"
    Expected Result: No sys.path found, script works, imports succeed
    Failure Indicators: sys.path still present, script fails, ImportError
    Evidence: .sisyphus/evidence/task-6-enricher-clean.log
  ```

  **Evidence to Capture**:
  - [ ] Grep showing no sys.path
  - [ ] Script help output

  **Commit**: YES (groups Tasks 5 and 6)
  - Message: `refactor(scripts): remove sys.path manipulation from orchestrator and enricher`
  - Files: `scripts/orchestrator.py`, `scripts/enricher.py`
  - Pre-commit: `python3 scripts/orchestrator.py --help && python3 scripts/enricher.py --help`

- [ ] 7. Replace print() in webhook_server.py

  **What to do**:
  - Add logging import at top: `import logging; logger = logging.getLogger(__name__)`
  - Replace 4 print() statements with logger calls
  - Line 84: `print(f"[WEBHOOK] Event: {event}")` → `logger.info(f"Webhook event: {event}", extra={"session": session})`
  - Line 142: `print(f"[webhook] Voice error: {e}")` → `logger.error(f"Voice processing error: {e}", exc_info=True)`
  - Line 191: `print(f"[WEBHOOK ERROR] {e}")` → `logger.error(f"Webhook error: {e}", exc_info=True)`
  - Line 775: `print("Starting...")` → `logger.info("Starting 1ai-reach API Server on port 8766")`

  **Must NOT do**:
  - Do NOT change webhook logic
  - Do NOT modify error handling
  - Do NOT add new dependencies

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple print replacement, single file
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 8, 9, 10)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:
  - AUDIT_REPORT.md:High Priority Issue #3
  - FIX_PROPOSALS.md:High Priority Fix #3

  **Acceptance Criteria**:
  - [ ] No print() in webhook_server.py: `grep "print(" webhook_server.py` returns nothing
  - [ ] Logger imported and configured
  - [ ] File compiles: `python3 -m py_compile webhook_server.py`

  **QA Scenarios**:
  ```
  Scenario: No print statements remain in webhook_server.py
    Tool: Bash (grep)
    Steps:
      1. Search for print: grep -n "print(" webhook_server.py
      2. Verify logger: grep "logger = logging.getLogger" webhook_server.py
    Expected Result: No print() found, logger configured
    Evidence: .sisyphus/evidence/task-7-no-print.log
  ```

  **Commit**: NO (groups with Task 8)

- [ ] 8. Replace print() in mcp_server.py

  **What to do**:
  - Add logging import: `import logging; logger = logging.getLogger(__name__)`
  - Replace 5 print() statements with logger.error()
  - Similar pattern to Task 7

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 7, 9, 10)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:
  - Same as Task 7

  **Acceptance Criteria**:
  - [ ] No print() in mcp_server.py
  - [ ] Logger configured
  - [ ] File compiles

  **QA Scenarios**:
  ```
  Scenario: No print statements in mcp_server.py
    Tool: Bash (grep)
    Steps:
      1. Search for print: grep -n "print(" mcp_server.py
    Expected Result: No print() found
    Evidence: .sisyphus/evidence/task-8-no-print.log
  ```

  **Commit**: YES (groups Tasks 7 and 8)
  - Message: `refactor(logging): replace print with logger in webhook and mcp servers`
  - Files: `webhook_server.py`, `mcp_server.py`
  - Pre-commit: `python3 -m py_compile webhook_server.py mcp_server.py`

- [ ] 9. Clean Old Workspace Paths

  **What to do**:
  - Remove stale generated files: `rm -rf docs/e2e-reports/dashboard/.next`
  - Rebuild dashboard: `cd dashboard && npm run build`
  - Verify no old paths: `grep -r "1ai-engage" dashboard/.next` returns nothing

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 7, 8, 10)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Task 2

  **References**:
  - AUDIT_REPORT.md:Critical Issue #3

  **Acceptance Criteria**:
  - [ ] Old .next directory removed
  - [ ] Dashboard rebuilds successfully
  - [ ] No old workspace paths in new build

  **QA Scenarios**:
  ```
  Scenario: Dashboard rebuild has correct paths
    Tool: Bash (grep + npm)
    Steps:
      1. Remove old: rm -rf docs/e2e-reports/dashboard/.next
      2. Rebuild: cd dashboard && npm run build
      3. Check paths: grep -r "1ai-engage" dashboard/.next
    Expected Result: Build succeeds, no old paths found
    Evidence: .sisyphus/evidence/task-9-clean-paths.log
  ```

  **Commit**: YES
  - Message: `fix(build): remove old workspace path references`
  - Files: None (removes generated files)
  - Pre-commit: `cd dashboard && npm run build`

- [ ] 10. Fix Package Name

  **What to do**:
  - Edit pyproject.toml line 6: change `name = "oneai-engage"` to `name = "oneai-reach"`
  - Reinstall package: `pip uninstall -y oneai-engage && pip install -e .`
  - Verify: `pip show oneai-reach`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 7, 8, 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:
  - AUDIT_REPORT.md:Medium Priority Issue #1

  **Acceptance Criteria**:
  - [ ] pyproject.toml has correct name
  - [ ] Package reinstalled with new name
  - [ ] `pip show oneai-reach` succeeds

  **QA Scenarios**:
  ```
  Scenario: Package name corrected
    Tool: Bash (pip)
    Steps:
      1. Check old package gone: pip show oneai-engage
      2. Check new package exists: pip show oneai-reach
      3. Verify imports still work: python3 -c "from oneai_reach.domain.models import Lead"
    Expected Result: Old package not found, new package installed, imports work
    Evidence: .sisyphus/evidence/task-10-package-name.log
  ```

  **Commit**: YES
  - Message: `fix(build): correct package name to oneai-reach`
  - Files: `pyproject.toml`
  - Pre-commit: `pip show oneai-reach`

- [ ] 11. Clean Build Artifacts

  **What to do**:
  - Remove Python artifacts: `find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null`
  - Remove .pyc files: `find . -type f -name "*.pyc" -delete`
  - Remove egg-info: `find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null`
  - Verify clean: `git status | grep -E "(__pycache__|\.pyc)"`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 12)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 12, 14
  - **Blocked By**: None

  **References**:
  - AUDIT_REPORT.md:Medium Priority Issue #2

  **Acceptance Criteria**:
  - [ ] All __pycache__ directories removed
  - [ ] All .pyc files removed
  - [ ] git status shows no build artifacts

  **QA Scenarios**:
  ```
  Scenario: Build artifacts cleaned
    Tool: Bash (find + git)
    Steps:
      1. Count before: find . -name "__pycache__" | wc -l
      2. Clean: find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
      3. Count after: find . -name "__pycache__" | wc -l
      4. Check git: git status --short | grep -E "(__pycache__|\.pyc)"
    Expected Result: Count drops to 0, git status clean
    Evidence: .sisyphus/evidence/task-11-clean-artifacts.log
  ```

  **Commit**: NO (groups with Task 12)

- [ ] 12. Update .gitignore

  **What to do**:
  - Append comprehensive ignore patterns to .gitignore
  - Add Python patterns: `__pycache__/`, `*.py[cod]`, `*.egg-info/`
  - Add Node patterns: `node_modules/`, `.next/`
  - Add IDE patterns: `.vscode/`, `.idea/`
  - Verify: `git check-ignore __pycache__` returns match

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 11)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 14
  - **Blocked By**: Task 11

  **References**:
  - FIX_PROPOSALS.md:Medium Priority Fix #2

  **Acceptance Criteria**:
  - [ ] .gitignore updated with comprehensive patterns
  - [ ] `git check-ignore __pycache__` matches
  - [ ] `git status` shows no untracked build artifacts

  **QA Scenarios**:
  ```
  Scenario: .gitignore prevents build artifacts
    Tool: Bash (git)
    Steps:
      1. Test Python: git check-ignore __pycache__
      2. Test Node: git check-ignore node_modules
      3. Check status: git status --short
    Expected Result: All patterns matched, status clean
    Evidence: .sisyphus/evidence/task-12-gitignore.log
  ```

  **Commit**: YES (groups Tasks 11 and 12)
  - Message: `chore: clean build artifacts and update gitignore`
  - Files: `.gitignore`
  - Pre-commit: `git check-ignore __pycache__ node_modules`

- [ ] 13. Verify All Services

  **What to do**:
  - Check API service: `systemctl status 1ai-reach-api.service`
  - Check dashboard service: `systemctl status 1ai-reach-dashboard.service`
  - Test API health: `curl http://localhost:8000/health`
  - Test dashboard: `curl http://localhost:8502`
  - Check logs for errors: `journalctl -u 1ai-reach-api.service -n 50`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Comprehensive verification, multiple services
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2

  **References**:
  - QUICK_FIX_GUIDE.md:Verification Checklist

  **Acceptance Criteria**:
  - [ ] Both services show "active (running)"
  - [ ] Health endpoint returns 200
  - [ ] Dashboard loads HTML
  - [ ] No errors in recent logs

  **QA Scenarios**:
  ```
  Scenario: All services running and healthy
    Tool: Bash (systemctl + curl)
    Steps:
      1. Check API: systemctl is-active 1ai-reach-api.service
      2. Check dashboard: systemctl is-active 1ai-reach-dashboard.service
      3. Test API: curl -f http://localhost:8000/health
      4. Test dashboard: curl -f http://localhost:8502 | grep "<html"
      5. Check logs: journalctl -u 1ai-reach-api.service -n 50 | grep -i error
    Expected Result: Both active, endpoints respond, no errors
    Evidence: .sisyphus/evidence/task-13-services-healthy.log
  ```

  **Commit**: YES
  - Message: `test: verify all services working`
  - Files: None
  - Pre-commit: None

---

## Final Verification Wave

After ALL implementation tasks complete, run comprehensive end-to-end verification:

- [ ] 14. End-to-End Integration Test

  **What to do**:
  - Restart all services from clean state
  - Test API health endpoint: `curl http://localhost:8000/health`
  - Test dashboard loads: `curl http://localhost:8502`
  - Verify no errors in logs: `journalctl -u 1ai-reach-api.service -n 100`
  - Test basic functionality (if possible without breaking production)
  - Generate comprehensive test report

  **Must NOT do**:
  - Do NOT test in production environment
  - Do NOT send real messages/emails
  - Do NOT modify any data

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Comprehensive testing, multiple systems, requires analysis
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (final verification)
  - **Parallel Group**: Wave FINAL
  - **Blocks**: None (last task)
  - **Blocked By**: ALL previous tasks (1-13)

  **References**:
  
  **Services to Test**:
  - API service (port 8000)
  - Dashboard service (port 8502)
  - Webhook server (if running)
  - Database connectivity
  
  **Verification Points**:
  - All systemd services active
  - All endpoints responding
  - No errors in logs
  - No import errors
  - No bare except clauses
  - No sys.path manipulation
  - No print statements in key files
  - Clean git status
  
  **Pattern Reference**:
  - QUICK_FIX_GUIDE.md:Verification Checklist
  - AUDIT_REPORT.md:Success Criteria

  **Acceptance Criteria**:
  
  - [ ] API service: `systemctl is-active 1ai-reach-api.service` returns "active"
  - [ ] Dashboard service: `systemctl is-active 1ai-reach-dashboard.service` returns "active"
  - [ ] Health endpoint: `curl -f http://localhost:8000/health` returns 200
  - [ ] Dashboard loads: `curl -s http://localhost:8502 | grep -q "<html"`
  - [ ] No import errors: `journalctl -u 1ai-reach-api.service -n 100 | grep -i importerror` returns nothing
  - [ ] No bare except: `grep -r "except:" src/oneai_reach/application/voice/` returns nothing
  - [ ] No sys.path in scripts: `grep "sys.path.insert" scripts/orchestrator.py scripts/enricher.py` returns nothing
  - [ ] No print in servers: `grep "print(" webhook_server.py mcp_server.py` returns nothing
  - [ ] Package installed: `pip show oneai-reach` succeeds
  - [ ] Clean git: `git status | grep -E "(__pycache__|\.pyc)"` returns nothing

  **QA Scenarios**:

  ```
  Scenario: All services running and healthy
    Tool: Bash (systemctl + curl)
    Preconditions: All fixes applied, services restarted
    Steps:
      1. Check API service: systemctl is-active 1ai-reach-api.service
      2. Check dashboard service: systemctl is-active 1ai-reach-dashboard.service
      3. Test API health: curl -f http://localhost:8000/health
      4. Test dashboard: curl -s http://localhost:8502 | head -20
      5. Verify HTML: curl -s http://localhost:8502 | grep -q "<html" && echo "OK"
    Expected Result: Both services active, health returns 200, dashboard returns HTML
    Failure Indicators: Service inactive, curl fails, no HTML
    Evidence: .sisyphus/evidence/task-14-services-running.log

  Scenario: No errors in recent logs
    Tool: Bash (journalctl + grep)
    Preconditions: Services running for at least 1 minute
    Steps:
      1. Get API logs: journalctl -u 1ai-reach-api.service -n 100 --no-pager
      2. Search for errors: journalctl -u 1ai-reach-api.service -n 100 | grep -i error
      3. Search for import errors: journalctl -u 1ai-reach-api.service -n 100 | grep -i importerror
      4. Search for exceptions: journalctl -u 1ai-reach-api.service -n 100 | grep -i exception
    Expected Result: No ImportError, minimal errors (only expected warnings)
    Failure Indicators: ImportError present, service crashes, repeated errors
    Evidence: .sisyphus/evidence/task-14-no-errors.log

  Scenario: All code quality fixes verified
    Tool: Bash (grep + find)
    Preconditions: All tasks 1-13 completed
    Steps:
      1. Check bare except: grep -r "except:" src/oneai_reach/application/voice/ | wc -l
      2. Check sys.path: grep "sys.path.insert" scripts/orchestrator.py scripts/enricher.py | wc -l
      3. Check print: grep "print(" webhook_server.py mcp_server.py | wc -l
      4. Check package: pip show oneai-reach | grep "Name: oneai-reach"
      5. Check artifacts: find . -name "__pycache__" | wc -l
    Expected Result: All counts are 0, package name correct
    Failure Indicators: Any count > 0, package not found
    Evidence: .sisyphus/evidence/task-14-quality-verified.log

  Scenario: Git repository clean
    Tool: Bash (git)
    Preconditions: Build artifacts cleaned, .gitignore updated
    Steps:
      1. Check status: git status --short
      2. Check untracked: git status --short | grep "^??"
      3. Check ignored: git check-ignore __pycache__ node_modules .next
      4. Count artifacts: git status --short | grep -E "(__pycache__|\.pyc)" | wc -l
    Expected Result: No untracked build artifacts, ignore patterns work, count is 0
    Failure Indicators: Build artifacts in git status
    Evidence: .sisyphus/evidence/task-14-git-clean.log
  ```

  **Evidence to Capture**:
  - [ ] Service status outputs
  - [ ] Health endpoint responses
  - [ ] Dashboard HTML snippet
  - [ ] Log excerpts (no errors)
  - [ ] Code quality verification results
  - [ ] Git status output
  - [ ] Comprehensive test report

  **Commit**: YES
  - Message: `test: comprehensive end-to-end integration verification`
  - Files: None (verification only)
  - Pre-commit: None

---

## Commit Strategy

**Atomic Commits** (one fix per commit):

1. `fix(api): correct import path for update_voice_config` — legacy.py
2. `build(dashboard): install missing npm dependencies` — package-lock.json
3. `fix(voice): replace bare except with specific exceptions` — 4 files
4. `build: install package in editable mode` — pip install -e .
5. `refactor(scripts): remove sys.path manipulation` — orchestrator.py, enricher.py
6. `refactor(logging): replace print with logger` — webhook_server.py, mcp_server.py
7. `fix(build): remove old workspace path references` — dashboard/.next
8. `fix(build): correct package name to oneai-reach` — pyproject.toml
9. `chore: clean build artifacts and update gitignore` — cleanup
10. `test: verify all services working` — integration test

**Pre-commit checks**:
- Python files: `python3 -m py_compile <file>`
- Services: `sudo systemctl restart <service> && systemctl status <service>`

---

## Success Criteria

### Verification Commands
```bash
# API service
systemctl status 1ai-reach-api.service
curl http://localhost:8000/health

# Dashboard service
systemctl status 1ai-reach-dashboard.service
curl http://localhost:8502

# Package installed
pip show oneai-reach

# No build artifacts
git status | grep -E "(__pycache__|\.pyc|node_modules)" && echo "FAIL" || echo "PASS"

# No bare except
grep -r "except:" src/oneai_reach/application/voice/ && echo "FAIL" || echo "PASS"

# No sys.path in scripts
grep -r "sys.path.insert" scripts/ && echo "FAIL" || echo "PASS"
```

### Final Checklist
- [ ] All "Must Have" items present
- [ ] All "Must NOT Have" items absent
- [ ] All services running without errors
- [ ] All tests passing
- [ ] All commits atomic and descriptive
- [ ] Documentation updated (if needed)
