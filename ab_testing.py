"""
A/B Testing for Routing
Test different routing strategies
"""
import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class ABExperiment:
    """A/B test experiment."""
    
    def __init__(
        self,
        name: str,
        variants: List[str],
        experiment_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/ab_experiments.json"
    ):
        self.name = name
        self.variants = variants
        self.experiment_file = experiment_file
        self.data = self._load()
        
        if name not in self.data:
            self.data[name] = {
                "variants": {v: {"users": [], "conversions": 0} for v in variants},
                "created_at": datetime.utcnow().isoformat()
            }
    
    def _load(self) -> Dict:
        if os.path.exists(self.experiment_file):
            with open(self.experiment_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.experiment_file), exist_ok=True)
        with open(self.experiment_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def get_variant(self, user_id: str) -> str:
        """Get assigned variant for user (deterministic)."""
        if self.name not in self.data:
            return self.variants[0]
        
        # Hash user_id to get deterministic assignment
        hash_input = f"{self.name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        variant_index = hash_value % len(self.variants)
        variant = self.variants[variant_index]
        
        # Track user assignment
        if user_id not in self.data[self.name]["variants"][variant]["users"]:
            self.data[self.name]["variants"][variant]["users"].append(user_id)
            self._save()
        
        return variant
    
    def record_conversion(self, user_id: str, variant: str):
        """Record a conversion for a variant."""
        if self.name in self.data and variant in self.data[self.name]["variants"]:
            self.data[self.name]["variants"][variant]["conversions"] += 1
            self._save()
    
    def get_stats(self) -> Dict:
        """Get experiment statistics."""
        if self.name not in self.data:
            return {}
        
        stats = {}
        
        for variant, data in self.data[self.name]["variants"].items():
            users = len(data["users"])
            conversions = data["conversions"]
            
            stats[variant] = {
                "users": users,
                "conversions": conversions,
                "conversion_rate": round(conversions / users, 3) if users > 0 else 0
            }
        
        return stats
    
    def get_winner(self) -> Optional[str]:
        """Get the winning variant."""
        stats = self.get_stats()
        
        if not stats:
            return None
        
        # Find variant with highest conversion rate
        winner = None
        best_rate = -1
        
        for variant, data in stats.items():
            if data["conversion_rate"] > best_rate:
                best_rate = data["conversion_rate"]
                winner = variant
        
        return winner


class ABTester:
    """Manage multiple A/B experiments."""
    
    def __init__(self):
        self.experiments: Dict[str, ABExperiment] = {}
    
    def create_experiment(self, name: str, variants: List[str]) -> ABExperiment:
        """Create a new experiment."""
        exp = ABExperiment(name, variants)
        self.experiments[name] = exp
        return exp
    
    def get_experiment(self, name: str) -> Optional[ABExperiment]:
        """Get existing experiment."""
        if name not in self.experiments:
            # Try to load from file
            try:
                self.experiments[name] = ABExperiment(name, [])
            except:
                return None
        
        return self.experiments[name]
    
    def assign(self, experiment_name: str, user_id: str) -> Optional[str]:
        """Assign user to variant."""
        exp = self.get_experiment(experiment_name)
        if exp:
            return exp.get_variant(user_id)
        return None
    
    def convert(self, experiment_name: str, user_id: str, variant: str):
        """Record conversion."""
        exp = self.get_experiment(experiment_name)
        if exp:
            exp.record_conversion(user_id, variant)


# Global tester
tester = ABTester()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "create":
            name = sys.argv[2]
            variants = sys.argv[3].split(",")
            exp = ABExperiment(name, variants)
            print(f"Created: {name} with variants {variants}")
        
        elif cmd == "assign":
            name = sys.argv[2]
            user = sys.argv[3]
            exp = ABExperiment(name, ["a", "b"])  # Load
            variant = exp.get_variant(user)
            print(f"User {user} → {variant}")
        
        elif cmd == "stats":
            name = sys.argv[2]
            exp = ABExperiment(name, ["a", "b"])
            print(json.dumps(exp.get_stats(), indent=2))
        
        elif cmd == "winner":
            name = sys.argv[2]
            exp = ABExperiment(name, ["a", "b"])
            print(f"Winner: {exp.get_winner()}")
    else:
        print("Usage: ab_testing.py <create|assign|stats|winner> [args]")