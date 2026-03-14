#!/bin/bash
# 🚀 Jarvis Quick-Start Script
# 
# This script starts both the Telegram bot + background tasks
# AND the HTTP API bridge in separate terminals.
#
# Usage:
#   chmod +x start.sh
#   ./start.sh
#
# Or on Windows:
#   python start.py (see start.py for Windows equivalent)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}          🚀 Jarvis Local Dev Environment             ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env (please edit with your credentials)${NC}"
    echo ""
fi

# Check Python environment
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python not found!${NC}"
    exit 1
fi

PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}Python: $($PYTHON_CMD --version)${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Verify telegram token
TELEGRAM_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" .env | cut -d '=' -f 2 | tr -d ' ')
if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" = "YOUR_TELEGRAM_BOT_TOKEN_HERE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: TELEGRAM_BOT_TOKEN not set!${NC}"
    echo "Edit .env and add your bot token from @BotFather"
    echo ""
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}              🎯 Starting Services                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Starting in 2 seconds... (Press Ctrl+C to cancel)"
echo ""
sleep 2

# Try to use tmux if available (cleaner UI)
if command -v tmux &> /dev/null; then
    echo -e "${GREEN}📺 Using tmux for multi-pane terminal${NC}"
    
    # Create new tmux session
    tmux new-session -d -s jarvis -x 120 -y 40
    
    # Pane 0: Main bot
    tmux send-keys -t jarvis:0 "echo '🤖 Starting Telegram Bot + Background Tasks...' && $PYTHON_CMD -m jarvis.main" Enter
    
    # Pane 1: API Bridge
    tmux new-window -t jarvis:1
    tmux send-keys -t jarvis:1 "echo '🌐 Starting HTTP API Bridge...' && sleep 2 && $PYTHON_CMD -m jarvis.api_bridge" Enter
    
    # Select first pane
    tmux select-window -t jarvis:0
    
    echo -e "${GREEN}✅ Jarvis is launching!${NC}"
    echo ""
    echo "📺 Tmux session 'jarvis' is running:"
    echo "   Window 0: Telegram bot (main.py)"
    echo "   Window 1: API bridge (api_bridge.py)"
    echo ""
    echo "Attach to the session:"
    echo -e "   ${YELLOW}tmux attach-session -t jarvis${NC}"
    echo ""
    echo "Switch panes:"
    echo -e "   ${YELLOW}Ctrl+B then 0 (first pane) or 1 (second pane)${NC}"
    echo ""
    exit 0
fi

# Fallback: Use simple background processes
echo -e "${YELLOW}⚠️  tmux not available, using background processes${NC}"
echo "⏳ This is not ideal—consider installing tmux for a better experience"
echo ""

# Start Telegram bot in background
echo -e "${YELLOW}Starting: Telegram Bot + Background Tasks...${NC}"
$PYTHON_CMD -m jarvis.main > logs/main.log 2>&1 &
MAIN_PID=$!
echo -e "${GREEN}✅ Main process (PID $MAIN_PID)${NC}"

sleep 2

# Start API Bridge in background
echo -e "${YELLOW}Starting: HTTP API Bridge...${NC}"
$PYTHON_CMD -m jarvis.api_bridge > logs/api_bridge.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✅ API Bridge process (PID $API_PID)${NC}"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}              ✨ All Services Running!                 ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🎯 Endpoints:"
echo -e "   API Health:    ${YELLOW}curl http://localhost:8000/api/health${NC}"
echo -e "   Send Command:  ${YELLOW}curl -X POST http://localhost:8000/api/command -H 'Content-Type: application/json' -d '{\"command\": \"/status\"}'${NC}"
echo ""
echo "📋 Logs:"
echo -e "   Main:    ${YELLOW}tail -f logs/main.log${NC}"
echo -e "   API:     ${YELLOW}tail -f logs/api_bridge.log${NC}"
echo ""
echo "🛑 To stop:"
echo -e "   ${YELLOW}kill $MAIN_PID $API_PID${NC}"
echo ""

# Keep script running and handle signals
trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $MAIN_PID $API_PID 2>/dev/null; echo -e '${GREEN}✅ Services stopped${NC}'; exit 0" INT TERM

while true; do
    sleep 1
done
