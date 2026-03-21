# Agent Delegation System - Technical Specification

## Intent Classifier Logic

### Overview
The intent classifier analyzes natural language input and determines the appropriate specialist agent to handle the request.

### Classification Algorithm

```
Input: Raw user request (string)
Output: Agent assignment + confidence score

1. Preprocessing
   - Lowercase normalization
   - Remove punctuation
   - Tokenize into words

2. Keyword Matching
   - Check against trigger keyword dictionary
   - Score = number of matching keywords per category

3. Disambiguation Rules
   - If multiple categories score equally:
     - Check for compound requests ("email and calendar")
     - Default to highest-priority category
     - Escalate to human review if tie persists

4. Confidence Threshold
   - >= 0.7: Auto-delegate
   - 0.4-0.69: Flag for review, still delegate
   - < 0.4: Escalate to Milo for manual routing
```

### Keyword Weighting
| Category | Primary Keywords | Weight |
|----------|-----------------|--------|
| Research | research, find, look up, search, what is, who is | 1.0 |
| Email | email, inbox, unsubscribe, gmail, mail, message | 1.0 |
| Shopping | order, buy, instacart, amazon, grocery, purchase | 1.0 |
| Calendar | calendar, schedule, remind, event, appointment | 1.0 |
| Health | water, walking, diet, calories, health, sleep, weight | 1.0 |
| Code | code, build, fix, script, create, programming | 1.0 |
| Review | review, check, verify, audit, test, validate | 1.0 |

## Agent Routing Rules

### Routing Priority Matrix
```
┌─────────────┬──────────────────┬─────────────────┐
│   Agent     │   Specialization │   Max Concurrent│
├─────────────┼──────────────────┼─────────────────┤
│ Archie      │ Research         │ 3               │
│ Merc        │ Communications   │ 5               │
│ Eris        │ Procurement      │ 2               │
│ Atro        │ Calendar         │ 5               │
│ Herc        │ Health/Wellness  │ 3               │
│ Heph        │ Coding           │ 2               │
│ Theo        │ Code Review      │ 3               │
└─────────────┴──────────────────┴─────────────────┘
```

### Routing Flow
1. Classify intent → get agent category
2. Check agent availability (concurrent task limit)
3. If available → delegate immediately
4. If busy → queue with priority
5. If agent offline → fallback to secondary agent or Milo

### Fallback Routing
| Primary Agent | Fallback Agent |
|--------------|----------------|
| Archie | Milo (manual) |
| Merc | Milo (manual) |
| Eris | Milo (manual) |
| Atro | Milo (manual) |
| Herc | Milo (manual) |
| Heph | Theo |
| Theo | Milo (manual) |

## Communication Protocols

### Inter-Agent Message Format
```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "from_agent": "milo",
  "to_agent": "archie",
  "task_type": "research",
  "payload": {
    "user_request": "string",
    "context": {},
    "priority": "normal|urgent|low",
    "callback_channel": "telegram"
  },
  "status": "pending|assigned|completed|failed"
}
```

### Delivery Guarantees
- **At-least-once delivery** for all agent messages
- **Retry policy**: 3 attempts with exponential backoff
- **Timeout**: 30 seconds for agent acknowledgment

### Status Updates
Agents report status via:
1. Direct callback to Milo
2. Write to shared memory file
3. Discord command center notification

## Error Handling

### Error Categories

| Error Type | Detection | Response |
|------------|-----------|----------|
| Agent timeout | No response in 30s | Re-queue or escalate |
| Agent unavailable | Max concurrent reached | Queue with priority |
| Classification failure | Confidence < 0.4 | Escalate to Milo |
| Communication failure | Message delivery failed | Retry 3x, then alert |
| Task rejection | Agent unable to complete | Re-route or escalate |

### Recovery Procedures

1. **Agent Timeout**
   ```
   1. Increment retry counter
   2. If retries < 3: re-delegate to same agent
   3. If retries >= 3: route to fallback agent
   4. If no fallback: escalate to Milo
   ```

2. **Communication Failure**
   ```
   1. Log error with message_id
   2. Store message in dead-letter queue
   3. Retry on next heartbeat
   4. Alert if persistent (>5 failures)
   ```

3. **Fallback Exhaustion**
   ```
   1. Milo takes ownership of task
   2. Attempt manual resolution
   3. Report back to user with explanation
   ```

## Memory Architecture

### Agent Memory Files
Each agent maintains:
- `memory/YYYY-MM-DD.md` - Daily activity log
- `MEMORY.md` - Long-term context
- `SOUL.md` - Persona and behavior rules

### Shared State
- `memory/delegation-queue.json` - Pending tasks
- `memory/agent-status.json` - Agent availability
- `memory/routing-log.md` - Delegation history

## Security Considerations

- Agents only access authorized resources per SOUL.md
- No cross-agent data sharing without explicit context
- All external actions require user consent (except routing)
- Audit log maintained for all delegations
