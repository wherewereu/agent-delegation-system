#!/bin/bash
# classify-intent.sh - Classify a user request and return recommended agent
# Usage: ./classify-intent.sh "<user_request>"
# Example: ./classify-intent.sh "is it going to rain today"

set -e

REQUEST="$1"

if [ -z "$REQUEST" ]; then
    echo "Usage: $0 \"<user_request>\""
    exit 1
fi

REQUEST_LOWER=$(echo "$REQUEST" | tr '[:upper:]' '[:lower:]')

declare -A SCORES
SCORES["archie"]=0
SCORES["merc"]=0
SCORES["eris"]=0
SCORES["atro"]=0
SCORES["herc"]=0
SCORES["heph"]=0
SCORES["theo"]=0

# Research keywords
for keyword in "research" "find" "look up" "search" "what is" "who is" "information"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["archie"]=$((SCORES["archie"] + 1))
    fi
done

# Communications keywords
for keyword in "email" "inbox" "unsubscribe" "gmail" "mail" "message" "send" "post"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["merc"]=$((SCORES["merc"] + 1))
    fi
done

# Shopping keywords
for keyword in "order" "buy" "instacart" "amazon" "grocery" "purchase" "shop"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["eris"]=$((SCORES["eris"] + 1))
    fi
done

# Calendar keywords
for keyword in "calendar" "schedule" "remind" "event" "appointment" "invite"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["atro"]=$((SCORES["atro"] + 1))
    fi
done

# Health keywords
for keyword in "water" "walking" "diet" "calories" "health" "sleep" "weight" "nutrition"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["herc"]=$((SCORES["herc"] + 1))
    fi
done

# Code keywords
for keyword in "code" "build" "fix" "script" "create" "program" "function" "automation"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["heph"]=$((SCORES["heph"] + 1))
    fi
done

# Review keywords
for keyword in "review" "check" "verify" "audit" "test" "validate" "approve"; do
    if echo "$REQUEST_LOWER" | grep -q "$keyword"; then
        SCORES["theo"]=$((SCORES["theo"] + 1))
    fi
done

# Find highest scoring agent
BEST_AGENT="milo"
BEST_SCORE=0
for agent in "${!SCORES[@]}"; do
    if [ ${SCORES[$agent]} -gt $BEST_SCORE ]; then
        BEST_SCORE=${SCORES[$agent]}
        BEST_AGENT=$agent
    fi
done

# Calculate confidence (normalize by request length approximation)
# Min score for auto-delegate is 1
if [ $BEST_SCORE -ge 2 ]; then
    CONFIDENCE="high"
elif [ $BEST_SCORE -eq 1 ]; then
    CONFIDENCE="medium"
else
    CONFIDENCE="low"
    BEST_AGENT="milo"
fi

echo "Classification Result:"
echo "  Agent: $BEST_AGENT"
echo "  Score: $BEST_SCORE"
echo "  Confidence: $CONFIDENCE"

if [ "$CONFIDENCE" = "low" ]; then
    echo "  Action: Escalate to Milo for manual routing"
elif [ "$CONFIDENCE" = "medium" ]; then
    echo "  Action: Delegate with monitoring"
else
    echo "  Action: Auto-delegate immediately"
fi

# Return agent name for scripting
echo "$BEST_AGENT"
