#!/bin/bash
# check-agent.sh - Check if an agent is available
# Usage: ./check-agent.sh <agent_name>
# Example: ./check-agent.sh archie

set -e

AGENT=$1

if [ -z "$AGENT" ]; then
    echo "Usage: $0 <agent_name>"
    exit 1
fi

declare -A MAX_CONCURRENT
MAX_CONCURRENT["archie"]=3
MAX_CONCURRENT["merc"]=5
MAX_CONCURRENT["eris"]=2
MAX_CONCURRENT["atro"]=5
MAX_CONCURRENT["herc"]=3
MAX_CONCURRENT["heph"]=2
MAX_CONCURRENT["theo"]=3

if [[ ! ${MAX_CONCURRENT[$AGENT]+exists} ]]; then
    echo "Error: Unknown agent '$AGENT'"
    exit 1
fi

MEMORY_FILE="$HOME/.openclaw/workspace/memory/agent-status.json"

if [ -f "$MEMORY_FILE" ]; then
    CURRENT_TASKS=$(cat "$MEMORY_FILE" | grep -o "\"${AGENT}\":[[:space:]]*[[:digit:]]*" | grep -o '[[:digit:]]*$' || echo "0")
else
    CURRENT_TASKS=0
fi

MAX=${MAX_CONCURRENT[$AGENT]}

echo "Agent: $AGENT"
echo "Current tasks: $CURRENT_TASKS"
echo "Max concurrent: $MAX"

if [ "$CURRENT_TASKS" -lt "$MAX" ]; then
    AVAILABLE_SLOTS=$((MAX - CURRENT_TASKS))
    echo "Status: AVAILABLE"
    echo "Available slots: $AVAILABLE_SLOTS"
    exit 0
else
    echo "Status: BUSY"
    echo "Available slots: 0"
    exit 1
fi
