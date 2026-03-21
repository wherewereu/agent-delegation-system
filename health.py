"""
Agent Health Monitoring
Tracks agent health, uptime, and implements circuit breaker
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class AgentHealth:
    """Track health metrics for each agent."""
    
    def __init__(self, health_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/health.json"):
        self.health_file = health_file
        self._ensure_file()
        self.data = self._load()
    
    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.health_file), exist_ok=True)
        if not os.path.exists(self.health_file):
            with open(self.health_file, "w") as f:
                json.dump({}, f)
    
    def _load(self) -> Dict:
        with open(self.health_file, "r") as f:
            return json.load(f)
    
    def _save(self):
        with open(self.health_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def _ensure_agent(self, agent: str):
        if agent not in self.data:
            self.data[agent] = {
                "active_tasks": [],
                "completed": 0,
                "failed": 0,
                "total_latency_ms": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def record_task_start(self, agent: str, task_id: str):
        """Record when a task starts"""
        self._ensure_agent(agent)
        if task_id not in self.data[agent]["active_tasks"]:
            self.data[agent]["active_tasks"].append(task_id)
        self.data[agent]["last_updated"] = datetime.utcnow().isoformat()
        self._save()
    
    def record_task_end(self, agent: str, task_id: str, status: str):
        """Record when a task ends"""
        self._ensure_agent(agent)
        
        # Remove from active
        if task_id in self.data[agent]["active_tasks"]:
            self.data[agent]["active_tasks"].remove(task_id)
        
        # Update stats
        if status == "success":
            self.data[agent]["completed"] = self.data[agent].get("completed", 0) + 1
        else:
            self.data[agent]["failed"] = self.data[agent].get("failed", 0) + 1
        
        self.data[agent]["last_updated"] = datetime.utcnow().isoformat()
        self._save()
    
    def get_stats(self, agent: str) -> Dict:
        """Get health stats for an agent"""
        self._ensure_agent(agent)
        data = self.data[agent]
        
        total = data.get("completed", 0) + data.get("failed", 0)
        success_rate = data.get("completed", 0) / total if total > 0 else 0
        
        return {
            "agent": agent,
            "total_tasks": total,
            "completed": data.get("completed", 0),
            "failed": data.get("failed", 0),
            "success_rate": round(success_rate, 2),
            "active": len(data.get("active_tasks", []))
        }
    
    def get_status(self, agent: str) -> Dict:
        """Get current status of an agent"""
        self._ensure_agent(agent)
        return {
            "agent": agent,
            "active": len(self.data[agent].get("active_tasks", [])),
            "status": "healthy" if len(self.data[agent].get("active_tasks", [])) < 5 else "busy",
            "last_updated": self.data[agent].get("last_updated")
        }
    
    def get_all_status(self) -> Dict:
        """Get status of all agents"""
        return {
            agent: self.get_status(agent)
            for agent in self.data.keys()
        }


class CircuitBreaker:
    """Circuit breaker for failing agents."""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_failure(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def record_success(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"
    
    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.recovery_timeout:
                    self.state = "half-open"
                    return False
            return True
        return False
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            return not self.is_open()  # Will be false until timeout
        elif self.state == "half-open":
            return True


class HealthMonitor:
    """Monitor health of all agents."""
    
    def __init__(self):
        self.health = AgentHealth()
        self.circuits = {}  # agent -> CircuitBreaker
    
    def get_circuit(self, agent: str) -> CircuitBreaker:
        if agent not in self.circuits:
            self.circuits[agent] = CircuitBreaker()
        return self.circuits[agent]
    
    def can_delegate(self, agent: str) -> bool:
        """Check if agent can accept new tasks"""
        # Check circuit breaker
        circuit = self.get_circuit(agent)
        if circuit.is_open():
            return False
        
        # Check active task count
        status = self.health.get_status(agent)
        return status["active"] < 10  # Max 10 concurrent
    
    def record_success(self, agent: str):
        """Record successful task"""
        circuit = self.get_circuit(agent)
        circuit.record_success()
    
    def record_failure(self, agent: str):
        """Record failed task"""
        circuit = self.get_circuit(agent)
        circuit.record_failure()


if __name__ == "__main__":
    import sys
    
    monitor = HealthMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            import json
            print(json.dumps(monitor.health.get_all_status(), indent=2))
        elif sys.argv[1] == "stats":
            import json
            stats = monitor.health.get_stats(sys.argv[2] if len(sys.argv) > 2 else "scout")
            print(json.dumps(stats, indent=2))
    else:
        print("Usage: health.py <status|stats> [agent]")