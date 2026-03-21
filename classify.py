"""
Intent Classification Module
Classifies user requests and routes to appropriate agent
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Agent(Enum):
    """Agent specializations - renamed from Justine's system"""
    SCOUT = "scout"       # Research
    LINK = "link"         # Communications
    CART = "cart"         # Procurement
    CLOCK = "clock"       # Calendar
    VITAL = "vital"       # Health
    FORGE = "forge"       # Code
    JUDGE = "judge"       # Review
    MILO = "milo"         # Orchestrator (fallback)


@dataclass
class ClassificationResult:
    """Result of intent classification"""
    agent: Agent
    confidence: float
    action: str  # "auto_delegate", "delegate_with_monitoring", "escalate"
    score: int


# Keyword mappings - each agent has trigger keywords
AGENT_KEYWORDS: Dict[Agent, List[str]] = {
    Agent.SCOUT: [
        "research", "find", "look up", "search", "what is", "who is", "information",
        "lookup", "fact", "facts", "find out", "get info"
    ],
    Agent.LINK: [
        "email", "inbox", "unsubscribe", "gmail", "mail", "message", "send",
        "post", "telegram", "discord", "signal", "text", "dm", "reply", "forward"
    ],
    Agent.CART: [
        "order", "buy", "instacart", "amazon", "grocery", "purchase", "shop",
        "shopping", "get me", "need", "restock", "delivery"
    ],
    Agent.CLOCK: [
        "calendar", "schedule", "remind", "event", "appointment", "invite",
        "meeting", "set up", "book", "reserve", "tomorrow", "later"
    ],
    Agent.VITAL: [
        "water", "walking", "diet", "calories", "health", "sleep", "weight",
        "nutrition", "exercise", "fitness", "wellness", "steps", "heart rate"
    ],
    Agent.FORGE: [
        "code", "build", "fix", "script", "create", "program", "function",
        "automation", "develop", "debug", "refactor", "implement"
    ],
    Agent.JUDGE: [
        "review", "check", "verify", "audit", "test", "validate", "approve",
        "quality", "inspect", "assess", "ensure"
    ],
}


def classify(request: str) -> ClassificationResult:
    """
    Classify a user request and determine the appropriate agent.
    
    Args:
        request: Raw user input string
        
    Returns:
        ClassificationResult with agent, confidence, and action
    """
    if not request or not request.strip():
        return ClassificationResult(
            agent=Agent.MILO,
            confidence=0.0,
            action="escalate",
            score=0
        )
    
    # Preprocess: lowercase and strip
    normalized = request.lower().strip()
    
    # Score each agent by keyword matches
    scores: Dict[Agent, int] = {agent: 0 for agent in Agent}
    
    for agent, keywords in AGENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[agent] += 1
    
    # Find agent with highest score
    best_agent = Agent.MILO
    best_score = 0
    
    # Priority order when scores are tied (higher = more specific)
    priority_order = [
        Agent.JUDGE,   # Review is specific
        Agent.FORGE,   # Code
        Agent.SCOUT,   # Research
        Agent.LINK,    # Comms
        Agent.CART,    # Shopping
        Agent.CLOCK,   # Calendar
        Agent.VITAL,   # Health
    ]
    
    for agent, score in scores.items():
        if score > best_score:
            best_score = score
            best_agent = agent
        elif score == best_score and score > 0:
            # Tie-breaker: check priority
            current_priority = priority_order.index(best_agent) if best_agent in priority_order else 999
            new_priority = priority_order.index(agent) if agent in priority_order else 999
            if new_priority < current_priority:
                best_agent = agent
    
    # Calculate confidence based on score
    # >= 2 keywords = high confidence (>=0.7)
    # == 1 keyword = medium confidence (0.4-0.69)
    # == 0 keywords = low confidence (<0.4)
    if best_score >= 2:
        confidence = min(0.7 + (best_score - 2) * 0.1, 1.0)
        action = "auto_delegate"
    elif best_score == 1:
        confidence = 0.4 + (best_score * 0.1)  # 0.5
        action = "delegate_with_monitoring"
    else:
        confidence = 0.0
        action = "escalate"
        best_agent = Agent.MILO
    
    return ClassificationResult(
        agent=best_agent,
        confidence=confidence,
        action=action,
        score=best_score
    )


def get_agent_max_concurrent(agent: Agent) -> int:
    """Get max concurrent tasks for an agent"""
    limits = {
        Agent.SCOUT: 3,
        Agent.LINK: 5,
        Agent.CART: 2,
        Agent.CLOCK: 5,
        Agent.VITAL: 3,
        Agent.FORGE: 2,
        Agent.JUDGE: 3,
        Agent.MILO: 1,
    }
    return limits.get(agent, 1)


def get_agent_fallback(agent: Agent) -> Agent:
    """Get fallback agent when primary is unavailable"""
    fallbacks = {
        Agent.SCOUT: Agent.MILO,
        Agent.LINK: Agent.MILO,
        Agent.CART: Agent.MILO,
        Agent.CLOCK: Agent.MILO,
        Agent.VITAL: Agent.MILO,
        Agent.FORGE: Agent.JUDGE,  # Code goes to review
        Agent.JUDGE: Agent.MILO,
    }
    return fallbacks.get(agent, Agent.MILO)


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = classify(request)
        print(f"Agent: {result.agent.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Action: {result.action}")
        print(f"Score: {result.score}")
    else:
        print("Usage: python classify.py \"your request here\"")


# ============================================================
# COMPOUND REQUEST HANDLING
# ============================================================

# Compound delimiters - words that suggest multiple tasks
COMPOUND_DELIMITERS = [" and ", ",", " plus ", " also ", " then ", "&"]


def classify_compound(request: str) -> List[Dict]:
    """
    Classify a request that may need multiple agents.
    
    Returns list of agent assignments with execution order.
    
    Args:
        request: Raw user input that may contain multiple tasks
        
    Returns:
        List of {"agent": str, "confidence": float, "task": str} 
        in execution order
    """
    if not request or not request.strip():
        return []
    
    # Try to split by compound delimiters
    parts = [request]
    for delimiter in COMPOUND_DELIMITERS:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(delimiter))
        parts = new_parts
    
    # Classify each part
    results = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        result = classify(part)
        
        # Only include if not escalation
        if result.agent != Agent.MILO:
            results.append({
                "agent": result.agent.value,
                "confidence": result.confidence,
                "task": part,
                "action": result.action
            })
    
    # Deduplicate agents (keep first occurrence)
    seen = set()
    unique_results = []
    for r in results:
        if r["agent"] not in seen:
            seen.add(r["agent"])
            unique_results.append(r)
    
    # Order by execution priority (Link -> Clock -> Cart -> Scout -> Forge -> Judge)
    execution_order = ["link", "clock", "cart", "scout", "forge", "judge", "vital"]
    
    def sort_key(r):
        return execution_order.index(r["agent"]) if r["agent"] in execution_order else 999
    
    unique_results.sort(key=sort_key)
    
    return unique_results