#!/bin/bash
pkill -f "mcp_server.py --transport http" 2>/dev/null || true
pkill -f "streamlit run ui/app.py" 2>/dev/null || true
echo "✅ All services stopped"
