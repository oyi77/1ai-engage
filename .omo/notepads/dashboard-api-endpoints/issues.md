
## Service Name Correction (2026-04-19)

### Issue
Initial implementation used incorrect systemd service names:
- Used `1ai-reach-webhook` but actual service is `1ai-reach-mcp`
- This would cause service restart/stop commands to fail

### Fix Applied
Updated all references in 3 locations:
1. `/src/oneai_reach/api/v1/admin.py` - status check (lines 206, 215)
2. `/src/oneai_reach/api/v1/agents.py` - restart command (line 554)
3. `/src/oneai_reach/api/v1/agents.py` - stop command (line 591)

Changed:
- Service name: `1ai-reach-webhook` → `1ai-reach-mcp`
- Label: "Webhook Server" → "Webhook/MCP Server"

### Verification
- ✓ Python syntax valid
- ✓ All 5 endpoints still registered
- ✓ Service commands now reference correct systemd unit

