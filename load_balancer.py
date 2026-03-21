"""
Load Balancer
Distribute tasks across multiple agent instances
"""
import random
from typing import Dict, List, Optional
from collections import defaultdict


class LoadBalancer:
    """Distribute tasks across agent instances."""
    
    def __init__(self):
        self.instances: Dict[str, List[str]] = defaultdict(list)
        self.health: Dict[str, Dict[str, bool]] = defaultdict(dict)
        self.current_index: Dict[str, int] = defaultdict(int)
    
    def register_instance(self, agent: str, instance_id: str):
        """Register a new agent instance."""
        if instance_id not in self.instances[agent]:
            self.instances[agent].append(instance_id)
            self.health[agent][instance_id] = True
    
    def unregister_instance(self, agent: str, instance_id: str):
        """Remove an agent instance."""
        if instance_id in self.instances[agent]:
            self.instances[agent].remove(instance_id)
            del self.health[agent][instance_id]
    
    def get_next_instance(self, agent: str) -> Optional[str]:
        """Get the next available instance (round-robin)."""
        if agent not in self.instances or not self.instances[agent]:
            return None
        
        # Get healthy instances
        healthy = [
            inst for inst in self.instances[agent]
            if self.health[agent].get(inst, True)
        ]
        
        if not healthy:
            return None
        
        # Round-robin through healthy instances
        index = self.current_index.get(agent, 0) % len(healthy)
        self.current_index[agent] = index + 1
        
        return healthy[index]
    
    def mark_healthy(self, agent: str, instance_id: str):
        """Mark an instance as healthy."""
        self.health[agent][instance_id] = True
    
    def mark_unhealthy(self, agent: str, instance_id: str):
        """Mark an instance as unhealthy."""
        self.health[agent][instance_id] = False
    
    def get_instances(self, agent: str) -> List[str]:
        """Get all registered instances for an agent."""
        return list(self.instances.get(agent, []))
    
    def get_healthy_count(self, agent: str) -> int:
        """Get count of healthy instances."""
        return sum(1 for inst in self.instances.get(agent, []) if self.health[agent].get(inst, True))
    
    def scale(self, agent: str, target_count: int):
        """Scale to target number of instances."""
        current = len(self.instances.get(agent, []))
        
        if current < target_count:
            # Add more instances
            for i in range(current, target_count):
                self.register_instance(agent, f"{agent}-instance-{i+1}")
        elif current > target_count:
            # Remove excess instances
            excess = current - target_count
            to_remove = self.instances[agent][:excess]
            for inst in to_remove:
                self.unregister_instance(agent, inst)
    
    def get_status(self) -> Dict:
        """Get load balancer status."""
        status = {}
        
        for agent in self.instances:
            status[agent] = {
                "total_instances": len(self.instances[agent]),
                "healthy_instances": self.get_healthy_count(agent),
                "instances": [
                    {
                        "id": inst,
                        "healthy": self.health[agent].get(inst, True)
                    }
                    for inst in self.instances[agent]
                ]
            }
        
        return status


if __name__ == "__main__":
    import sys
    
    lb = LoadBalancer()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "register":
            lb.register_instance(sys.argv[2], sys.argv[3])
            print(f"Registered {sys.argv[3]} for {sys.argv[2]}")
        
        elif cmd == "next":
            inst = lb.get_next_instance(sys.argv[2])
            print(f"Next instance: {inst}")
        
        elif cmd == "status":
            import json
            print(json.dumps(lb.get_status(), indent=2))
        
        elif cmd == "scale":
            lb.scale(sys.argv[2], int(sys.argv[3]))
            print(f"Scaled {sys.argv[2]} to {sys.argv[3]} instances")
    else:
        print("Usage: load_balancer.py <register|next|status|scale> <agent> [args]")