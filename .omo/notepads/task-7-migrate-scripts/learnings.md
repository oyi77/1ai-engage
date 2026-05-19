# Task 7: Migrate Scripts to Application Layer - Learnings

## Part 2b: Reviewer Service Migration (2026-04-17)

### What Was Done
- Migrated `scripts/reviewer.py` → `src/oneai_reach/application/outreach/reviewer_service.py`
- Created `ReviewerService` class with dependency injection (Settings)
- Extracted all business logic: prompt building, Claude calling, output parsing, scoring
- Updated original script to thin CLI wrapper calling service
- Added ReviewerService to `__init__.py` exports

### Key Patterns Applied
- Service receives Settings via constructor (matches Parts 1 & 2a)
- Uses structured logging with get_logger()
- Raises ExternalAPIError for Claude failures
- Preserves exact functionality (6+ pass threshold, 1-10 scoring)
- Original script remains backward compatible

### Technical Details
- Claude review via subprocess (will be abstracted in Task 13)
- Scoring criteria: personalization, pain points, value prop, CTA, tone
- Error handling: returns ERROR verdict with issues list on failure
- Helper methods: `is_passing()`, `format_issues()` for clean separation

### Error Fixed
- Initial bug: `e.reason` → `e.message` (ExternalAPIError attribute)
- All tests pass: import, instantiation, method calls, backward compatibility

### Verification Results
✓ ReviewerService imports successfully
✓ All service methods work (build_prompt, parse_output, is_passing, format_issues)
✓ Original script imports and runs without errors
✓ Backward compatibility maintained (PASS_THRESHOLD=6)
✓ Integration with other outreach services confirmed
