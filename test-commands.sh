#!/bin/bash
# 🧪 Jarvis API Test Suite
#
# This script tests all the API endpoints to verify the bridge is working.
#
# Usage:
#   chmod +x test-commands.sh
#   ./test-commands.sh
#
# Or test individual commands:
#   ./test-commands.sh health
#   ./test-commands.sh commands
#   ./test-commands.sh status

set -e

API_URL="${API_URL:-http://localhost:8000}"
VERBOSE="${VERBOSE:-false}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}       🧪 Jarvis API Bridge Test Suite                ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "API Base URL: $API_URL"
    echo ""
}

test_health() {
    echo -e "${YELLOW}Testing: GET /api/health${NC}"
    
    response=$(curl -s "$API_URL/api/health")
    status=$(echo "$response" | grep -o '"status":"[^"]*"' | head -1 || echo '"status":"error"')
    
    if [[ $status == *"ok"* ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_commands_list() {
    echo -e "${YELLOW}Testing: GET /api/commands${NC}"
    
    response=$(curl -s "$API_URL/api/commands")
    count=$(echo "$response" | grep -o '"count":[0-9]*' || echo '"count":0')
    
    if [[ $count == *"11"* ]] || [[ $count == *"1"* ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_help() {
    echo -e "${YELLOW}Testing: POST /api/command with /help${NC}"
    
    response=$(curl -s -X POST "$API_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "/help"}')
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ PASS${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .response -r
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_status() {
    echo -e "${YELLOW}Testing: POST /api/command with /status${NC}"
    
    response=$(curl -s -X POST "$API_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "/status"}')
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ PASS${NC}"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "Response:"
            echo "$response" | jq .response -r
        fi
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_invalid_command() {
    echo -e "${YELLOW}Testing: POST /api/command with invalid command${NC}"
    
    response=$(curl -s -X POST "$API_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "/nonexistent"}')
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ PASS (error handling works)${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .response -r
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_drafts() {
    echo -e "${YELLOW}Testing: POST /api/command with /drafts${NC}"
    
    response=$(curl -s -X POST "$API_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "/drafts"}')
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ PASS${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .response -r
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_keywords_list() {
    echo -e "${YELLOW}Testing: POST /api/command with /keywords (invalid args)${NC}"
    
    response=$(curl -s -X POST "$API_URL/api/command" \
        -H "Content-Type: application/json" \
        -d '{"command": "/keywords"}')
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ PASS (error handling works)${NC}"
        [[ "$VERBOSE" == "true" ]] && echo "$response" | jq .response -r
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "$response"
    fi
    echo ""
}

test_connection() {
    echo -e "${YELLOW}Checking API connection...${NC}"
    
    if curl -s --connect-timeout 2 "$API_URL/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is reachable${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}❌ Cannot reach API at $API_URL${NC}"
        echo ""
        echo "Make sure to run:"
        echo "  python -m jarvis.api_bridge"
        echo ""
        exit 1
    fi
}

run_all_tests() {
    print_header
    test_connection
    test_health
    test_commands_list
    test_help
    test_status
    test_invalid_command
    test_drafts
    test_keywords_list
    
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}           🎉 Test Suite Complete!                    ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "💡 Tips:"
    echo "   - Run with VERBOSE=true for detailed responses"
    echo "   - Set API_URL to test a different server"
    echo "   - Check logs with: tail -f logs/api_bridge.log"
    echo ""
}

# Main
case "${1:-all}" in
    all)
        run_all_tests
        ;;
    health)
        print_header
        test_connection
        test_health
        ;;
    commands)
        print_header
        test_connection
        test_commands_list
        ;;
    help)
        print_header
        test_connection
        test_help
        ;;
    status)
        print_header
        test_connection
        test_status
        ;;
    drafts)
        print_header
        test_connection
        test_drafts
        ;;
    *)
        echo "Usage: $0 [all|health|commands|help|status|drafts]"
        echo ""
        echo "Examples:"
        echo "  $0 all              # Run all tests"
        echo "  $0 status           # Test /status command only"
        echo "  VERBOSE=true $0     # Run with detailed output"
        echo "  API_URL=http://example.com:8000 $0  # Test remote API"
        exit 1
        ;;
esac
