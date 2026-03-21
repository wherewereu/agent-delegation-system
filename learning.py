"""
Learning Engine
Learn from delegation patterns to improve routing
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class LearningEngine:
    """Learn from delegation patterns to improve routing decisions."""
    
    def __init__(self, history_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/learning.json"):
        self.history_file = history_file
        self._ensure_file()
        self.history = self._load()
    
    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as f:
                json.dump([], f)
    
    def _load(self) -> List[Dict]:
        with open(self.history_file, "r") as f:
            return json.load(f)
    
    def _save(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)
    
    def record(
        self,
        request: str,
        agent: str,
        success: bool,
        latency_ms: int = 0
    ):
        """Record a delegation result for learning."""
        # Normalize request (lowercase, strip)
        request_key = request.lower().strip()[:50]
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request": request_key,
            "agent": agent,
            "success": success,
            "latency_ms": latency_ms
        }
        
        self.history.append(entry)
        
        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self._save()
    
    def get_history(self) -> List[Dict]:
        """Get all recorded history."""
        return self.history
    
    def get_best_agent(self, request: str) -> Optional[str]:
        """Get the best performing agent for a request type."""
        request_key = request.lower().strip()[:50]
        
        # Find all records for this request
        matches = [h for h in self.history if request_key in h["request"]]
        
        if not matches:
            return None
        
        # Score each agent
        agent_scores = defaultdict(lambda: {"success": 0, "total": 0, "avg_latency": 0})
        
        for match in matches:
            agent = match["agent"]
            agent_scores[agent]["total"] += 1
            if match["success"]:
                agent_scores[agent]["success"] += 1
        
        # Find agent with highest success rate
        best_agent = None
        best_rate = -1
        
        for agent, scores in agent_scores.items():
            if scores["total"] >= 2:  # Minimum sample size
                rate = scores["success"] / scores["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_agent = agent
        
        return best_agent
    
    def get_adjusted_confidence(
        self,
        agent: str,
        request: str,
        base_confidence: float
    ) -> float:
        """Adjust confidence based on historical success."""
        request_key = request.lower().strip()[:50]
        
        # Find records for this agent + request
        matches = [
            h for h in self.history
            if h["agent"] == agent and request_key in h["request"]
        ]
        
        if not matches:
            return base_confidence
        
        # Calculate success rate
        successes = sum(1 for m in matches if m["success"])
        rate = successes / len(matches)
        
        # Adjust confidence
        # If 100% success, boost by up to 0.2
        # If 0% success, reduce by up to 0.3
        adjustment = (rate - 0.5) * 0.4  # -0.2 to +0.2
        
        adjusted = base_confidence + adjustment
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, adjusted))
    
    def get_stats(self) -> Dict:
        """Get learning statistics."""
        if not self.history:
            return {"total_records": 0, "agents": [], "avg_success_rate": 0}
        
        agent_counts = defaultdict(lambda: {"success": 0, "total": 0})
        
        for entry in self.history:
            agent_counts[entry["agent"]]["total"] += 1
            if entry["success"]:
                agent_counts[entry["agent"]]["success"] += 1
        
        total_success = sum(a["success"] for a in agent_counts.values())
        total = sum(a["total"] for a in agent_counts.values())
        
        return {
            "total_records": len(self.history),
            "agents": list(agent_counts.keys()),
            "avg_success_rate": round(total_success / total if total > 0 else 0, 2)
        }


if __name__ == "__main__":
    import sys
    
    engine = LearningEngine()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            import json
            print(json.dumps(engine.get_stats(), indent=2))
        elif sys.argv[1] == "best":
            if len(sys.argv) > 2:
                print(engine.get_best_agent(sys.argv[2]))
    else:
        print("Usage: learning.py <stats|best> [request]")