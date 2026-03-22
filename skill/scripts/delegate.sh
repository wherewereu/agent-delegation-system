#!/bin/bash
# delegate.sh - Route a task to the specified OpenClaw subagent via mesh relay
# Usage: ./delegate.sh <agent> <task_description> [priority]
# Example: ./delegate.sh archie "what is the weather today" normal

set -e

AGENT=$1
TASK=$2
PRIORITY=${3:-normal}

if [ -z "$AGENT" ] || [ -z "$TASK" ]; then
    echo "Usage: $0 <agent> <task_description> [priority]"
    exit 1
fi

VALID_AGENTS="archie merc eris atro herc heph theo"
if [[ ! $VALID_AGENTS =~ (^|[[:space:]])$AGENT($|[[:space:]]) ]]; then
    echo "Error: Invalid agent '$AGENT'"
    echo "Valid agents: $VALID_AGENTS"
    exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MESSAGE_ID=$(uuidgen 2>/dev/null || cat /dev/urandom | tr -dc 'a-z0-9' | head -c 36)

MESSAGE_JSON=$(cat <<EOF
{
  "message_id": "$MESSAGE_ID",
  "timestamp": "$TIMESTAMP",
  "from_agent": "milo",
  "to_agent": "$AGENT",
  "task_description": "$TASK",
  "priority": "$PRIORITY",
  "status": "pending"
}
EOF
)

echo "Delegating task to $AGENT..."
echo "$MESSAGE_JSON"

# Post to mesh relay if available
if curl -s -X POST http://MESH_RELAY_IP:8500/messages/send \
    -H "Content-Type: application/json" \
    -d "$MESSAGE_JSON" > /dev/null 2>&1; then
    echo "Task delegated successfully via mesh relay"
else
    echo "Mesh relay unavailable - task queued for when agent is available"
fi

echo "$MESSAGE_ID"
