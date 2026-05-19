## API Endpoints Implementation (2026-04-19)

### Implemented Endpoints

1. **POST /api/v1/agents/autonomous/start**
   - Request: `{ dry_run: bool, run_once: bool }`
   - Calls `agent_control.start_background_stage("autonomous_loop", args)`
   - Returns job info with status

2. **POST /api/v1/agents/autonomous/stop**
   - Finds running autonomous_loop job via `agent_control.list_jobs()`
   - Calls `agent_control.stop_job(job_id)`
   - Returns stop confirmation

3. **POST /api/v1/agents/services/{key}/restart**
   - Supports: webhook, dashboard
   - Uses systemctl restart commands
   - Returns success/error with command details

4. **POST /api/v1/agents/services/{key}/stop**
   - Supports: webhook, dashboard
   - Uses systemctl stop commands
   - Returns success/error with command details

5. **GET /api/v1/admin/status**
   - Returns `{ services: ServiceStatus[] }`
   - ServiceStatus: `{ key, label, running, pid?, port? }`
   - Checks systemctl status for webhook/dashboard
   - Checks agent_control jobs for autonomous loop

### Key Patterns

- All endpoints use `AgentResponse` model for consistency
- Service management uses subprocess with timeout protection
- Status endpoint queries both systemctl and agent_control
- Proper error handling with HTTPException
- Models validated with Pydantic

### Testing

- Python syntax: ✓ Valid
- Module imports: ✓ Successful
- Dashboard build: ✓ No TypeScript errors
- Pydantic models: ✓ Validated
- Route registration: ✓ All 5 endpoints registered
