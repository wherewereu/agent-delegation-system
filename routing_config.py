"""
Natural Language Routing Rules
Configure routing via declarative rules
"""
import json
import os
import re
from typing import Dict, List, Optional


class RoutingRule:
    """A routing rule definition."""
    
    def __init__(
        self,
        rule_id: str,
        condition: str,
        agent: str,
        priority: int = 5
    ):
        self.rule_id = rule_id
        self.condition = condition
        self.agent = agent
        self.priority = priority
    
    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "condition": self.condition,
            "agent": self.agent,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RoutingRule":
        return cls(
            rule_id=data["rule_id"],
            condition=data["condition"],
            agent=data["agent"],
            priority=data.get("priority", 5)
        )


class RoutingRuleEngine:
    """Engine for evaluating routing rules."""
    
    def __init__(self, rules_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/routing_rules.json"):
        self.rules_file = rules_file
        self.rules: List[RoutingRule] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load rules from file."""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, "r") as f:
                data = json.load(f)
                self.rules = [RoutingRule.from_dict(r) for r in data.get("rules", [])]
    
    def _save_rules(self):
        """Save rules to file."""
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        with open(self.rules_file, "w") as f:
            json.dump({"rules": [r.to_dict() for r in self.rules]}, f, indent=2)
    
    def add_rule(self, condition: str, agent: str, priority: int = 5) -> Dict:
        """Add a new routing rule."""
        import uuid
        rule = RoutingRule(
            rule_id=str(uuid.uuid4()),
            condition=condition,
            agent=agent,
            priority=priority
        )
        self.rules.append(rule)
        self._save_rules()
        return rule.to_dict()
    
    def match(self, request: str) -> Optional[str]:
        """Match request against rules, return agent or None."""
        if not self.rules:
            return None
        
        # Sort by priority (highest first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        
        request_lower = request.lower()
        
        for rule in sorted_rules:
            if self._evaluate_condition(rule.condition, request_lower):
                return rule.agent
        
        return None
    
    def _evaluate_condition(self, condition: str, request: str) -> bool:
        """Evaluate a single condition."""
        condition = condition.lower()
        
        # Parse condition type
        if condition.startswith("contains keyword "):
            keyword = condition.replace("contains keyword ", "")
            return keyword in request
        
        elif condition.startswith("starts with "):
            prefix = condition.replace("starts with ", "")
            return request.startswith(prefix)
        
        elif condition.startswith("ends with "):
            suffix = condition.replace("ends with ", "")
            return request.endswith(suffix)
        
        elif condition.startswith("matches regex "):
            pattern = condition.replace("matches regex ", "")
            return bool(re.search(pattern, request))
        
        elif " contains " in condition:
            # "X contains Y" format
            parts = condition.split(" contains ")
            if len(parts) == 2:
                return parts[1].strip() in parts[0].strip()
        
        # Default: contains the whole phrase
        return condition in request
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        before = len(self.rules)
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        
        if len(self.rules) < before:
            self._save_rules()
            return True
        return False
    
    def list_rules(self) -> List[Dict]:
        """List all rules."""
        return [r.to_dict() for r in sorted(self.rules, key=lambda r: r.priority, reverse=True)]


if __name__ == "__main__":
    import sys
    
    engine = RoutingRuleEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "list":
            rules = engine.list_rules()
            print(f"Rules ({len(rules)}):")
            for r in rules:
                print(f"  [{r['priority']}] {r['condition']} → {r['agent']}")
        
        elif cmd == "add":
            condition = sys.argv[2]
            agent = sys.argv[3]
            priority = int(sys.argv[4]) if len(sys.argv) > 4 else 5
            rule = engine.add_rule(condition, agent, priority)
            print(f"Added: {rule}")
        
        elif cmd == "match":
            request = " ".join(sys.argv[2:])
            match = engine.match(request)
            print(f"Match: {match}")
    else:
        print("Usage: routing_config.py <list|add|match> [args]")