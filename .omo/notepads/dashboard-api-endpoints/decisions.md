## Implementation Decisions

### Endpoint Placement
- Autonomous endpoints: `/api/v1/agents/autonomous/*` (in agents.py)
- Service management: `/api/v1/agents/services/{key}/*` (in agents.py)
- Status endpoint: `/api/v1/admin/status` (updated in admin.py)

Rationale: Agents.py already handles job/stage management, so autonomous control fits naturally there. Admin.py handles system-wide status, so service status belongs there.

### Service Management Approach
- Used systemctl commands for webhook/dashboard (systemd services)
- Used agent_control jobs for autonomous loop (background process)

Rationale: Webhook and dashboard run as systemd services, while autonomous loop is managed via agent_control's job system.

### Status Endpoint Design
- Changed from conversation info to service status list
- Returns array of ServiceStatus objects with key, label, running, pid, port

Rationale: Dashboard expects service status, not conversation info. The old endpoint was returning wrong data type.

### Error Handling
- HTTPException with proper status codes (400, 404, 500)
- Timeout protection on subprocess calls (10s)
- Graceful fallback when services not found

Rationale: Prevents hanging on systemctl calls and provides clear error messages to dashboard.
