#!/bin/bash
# Setup systemd services for 1ai-engage auto-start on boot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Setting up systemd services for 1ai-engage..."
echo ""

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Copy service files
echo "📋 Installing service files..."
sudo cp "$PROJECT_DIR/systemd/"*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable 1ai-engage-mcp.service
sudo systemctl enable 1ai-engage-ui.service
sudo systemctl enable 1ai-engage-watchdog.service

echo ""
echo "✅ Systemd services installed!"
echo ""
echo "Commands:"
echo "  sudo systemctl start 1ai-engage-mcp    # Start MCP Server"
echo "  sudo systemctl start 1ai-engage-ui       # Start Streamlit UI"
echo "  sudo systemctl start 1ai-engage-watchdog # Start Watchdog"
echo "  sudo systemctl status 1ai-engage-*       # Check status"
echo ""
echo "Or use: ./scripts/start_all.sh"
echo ""
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start 1ai-engage-mcp
    sudo systemctl start 1ai-engage-ui
    sudo systemctl start 1ai-engage-watchdog
    echo ""
    echo "✅ Services started!"
    sleep 2
    sudo systemctl status 1ai-engage-mcp --no-pager
fi
