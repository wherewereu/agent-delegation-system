"""
Agent State Management
Tracks agent availability, task counts, and routing
"""
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime


class TaskStatus:
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    agent: str
    description: str
    priority: str = "normal"
    status: str = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None


# Max concurrent tasks per agent
AGENT_LIMITS = {
    "scout": 3,
    "link": 5,
    "cart": 2,
    "clock": 5,
    "vital": 3,
    "forge": 2,
    "judge": 3,
    "milo": 1,
}

# Fallback routing when primary is unavailable
AGENT_FALLBACKS = {
    "scout": "milo",
    "link": "milo",
    "cart": "milo",
    "clock": "milo",
    "vital": "milo",
    "forge": "judge",  # Code goes to review
    "judge": "milo",
}


class AgentState:
    """Manages agent availability and task tracking."""
    
    def __init__(self):
        self.current_tasks: Dict[str, List[str]] = {}  # agent -> [task_ids]
        self.tasks: Dict[str, Task] = {}  # task_id -> Task
    
    def is_available(self, agent: str) -> bool:
        """Check if agent has available slots"""
        if agent not in AGENT_LIMITS:
            return False
        
        current = len(self.current_tasks.get(agent, []))
        return current < AGENT_LIMITS[agent]
    
    def get_available_slots(self, agent: str) -> int:
        """Get number of available slots for agent"""
        if agent not in AGENT_LIMITS:
            return 0
        
        current = len(self.current_tasks.get(agent, []))
        return max(0, AGENT_LIMITS[agent] - current)
    
    def add_task(self, agent: str, task_id: str, priority: str = "normal") -> bool:
        """Add a task to an agent. Returns False if agent unavailable."""
        if not self.is_available(agent):
            return False
        
        if agent not in self.current_tasks:
            self.current_tasks[agent] = []
        
        self.current_tasks[agent].append(task_id)
        
        self.tasks[task_id] = Task(
            task_id=task_id,
            agent=agent,
            description="",
            priority=priority,
            status=TaskStatus.PENDING
        )
        
        return True
    
    def complete_task(self, agent: str, task_id: str) -> bool:
        """Mark a task as completed and free the slot"""
        if task_id not in self.tasks:
            return False
        
        # Remove from agent's task list
        if agent in self.current_tasks and task_id in self.current_tasks[agent]:
            self.current_tasks[agent].remove(task_id)
        
        # Update task status
        self.tasks[task_id].status = TaskStatus.COMPLETED
        self.tasks[task_id].completed_at = datetime.utcnow().isoformat()
        
        return True
    
    def fail_task(self, agent: str, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        if task_id not in self.tasks:
            return False
        
        # Remove from agent's task list
        if agent in self.current_tasks and task_id in self.current_tasks[agent]:
            self.current_tasks[agent].remove(task_id)
        
        # Update task status
        self.tasks[task_id].status = TaskStatus.FAILED
        self.tasks[task_id].error = error
        
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "agent": task.agent,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "error": task.error
        }
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks sorted by priority"""
        priority_order = {"urgent": 0, "normal": 1, "low": 2}
        
        pending = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                pending.append({
                    "task_id": task_id,
                    "agent": task.agent,
                    "description": task.description,
                    "priority": task.priority,
                    "created_at": task.created_at
                })
        
        # Sort by priority
        pending.sort(key=lambda x: priority_order.get(x["priority"], 1))
        
        return pending
    
    def get_fallback(self, agent: str) -> str:
        """Get fallback agent when primary is unavailable"""
        return AGENT_FALLBACKS.get(agent, "milo")
    
    def get_agent_load(self, agent: str) -> Dict:
        """Get current load info for an agent"""
        return {
            "agent": agent,
            "current": len(self.current_tasks.get(agent, [])),
            "max": AGENT_LIMITS.get(agent, 0),
            "available": self.get_available_slots(agent)
        }
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "current_tasks": self.current_tasks,
            "tasks": {k: asdict(v) for k, v in self.tasks.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentState":
        """Deserialize from dictionary"""
        state = cls()
        state.current_tasks = data.get("current_tasks", {})
        
        for task_id, task_data in data.get("tasks", {}).items():
            state.tasks[task_id] = Task(**task_data)
        
        return state
    
    def save(self, filepath: str):
        """Save state to JSON file"""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "AgentState":
        """Load state from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


# CLI interface
if __name__ == "__main__":
    import sys
    
    state = AgentState()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "available":
            agent = sys.argv[2] if len(sys.argv) > 2 else None
            if agent:
                print(f"{agent}: {state.is_available(agent)}")
            else:
                for a in AGENT_LIMITS:
                    print(f"{a}: {state.is_available(a)} (slots: {state.get_available_slots(a)})")
        
        elif cmd == "add":
            agent = sys.argv[2]
            task_id = sys.argv[3] if len(sys.argv) > 3 else "task-1"
            state.add_task(agent, task_id)
            print(f"Added task {task_id} to {agent}")
        
        elif cmd == "complete":
            agent = sys.argv[2]
            task_id = sys.argv[3]
            state.complete_task(agent, task_id)
            print(f"Completed task {task_id}")
        
        elif cmd == "status":
            task_id = sys.argv[2]
            status = state.get_task_status(task_id)
            print(json.dumps(status, indent=2))
    else:
        print("Usage: python state.py <command> [args]")
        print("Commands: available, add, complete, status")


# ============================================================
# RETRY LOGIC & DEAD-LETTER QUEUE
# ============================================================

import os

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1  # seconds


def calculate_backoff(attempt: int) -> int:
    """Calculate exponential backoff delay"""
    return RETRY_BASE_DELAY * (2 ** attempt)


def dead_letter_queue_add(
    task_id: str,
    agent: str,
    error: str,
    original_request: str,
    priority: str = "normal",
    dlq_file: str = "/tmp/dead-letter.json"
):
    """Add a failed task to the dead-letter queue"""
    os.makedirs(os.path.dirname(dlq_file) if os.path.dirname(dlq_file) else "/tmp", exist_ok=True)
    
    # Load existing DLQ
    dlq = {}
    if os.path.exists(dlq_file):
        with open(dlq_file, "r") as f:
            dlq = json.load(f)
    
    # Add failed task
    dlq[task_id] = {
        "task_id": task_id,
        "agent": agent,
        "error": error,
        "original_request": original_request,
        "priority": priority,
        "failed_at": datetime.utcnow().isoformat(),
        "retry_count": 0
    }
    
    # Save DLQ
    with open(dlq_file, "w") as f:
        json.dump(dlq, f, indent=2)


def dead_letter_queue_list(dlq_file: str = "/tmp/dead-letter.json") -> List[Dict]:
    """List all tasks in the dead-letter queue"""
    if not os.path.exists(dlq_file):
        return []
    
    with open(dlq_file, "r") as f:
        dlq = json.load(f)
    
    return list(dlq.values())


def dead_letter_queue_retry(task_id: str, dlq_file: str = "/tmp/dead-letter.json") -> Optional[Dict]:
    """Retry a task from the dead-letter queue (removes from DLQ)"""
    if not os.path.exists(dlq_file):
        return None
    
    with open(dlq_file, "r") as f:
        dlq = json.load(f)
    
    if task_id not in dlq:
        return None
    
    task_info = dlq[task_id]
    
    # Remove from DLQ
    del dlq[task_id]
    
    with open(dlq_file, "w") as f:
        json.dump(dlq, f, indent=2)
    
    return task_info