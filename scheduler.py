"""
Task Scheduler
Schedule tasks for delayed execution
"""
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ScheduledTask:
    """Represents a scheduled task."""
    
    def __init__(
        self,
        task_id: str,
        agent: str,
        request: str,
        run_at: datetime,
        priority: str = "normal"
    ):
        self.task_id = task_id
        self.agent = agent
        self.request = request
        self.run_at = run_at
        self.priority = priority
        self.status = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "agent": self.agent,
            "request": self.request,
            "run_at": self.run_at.isoformat(),
            "priority": self.priority,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ScheduledTask":
        task = cls(
            task_id=data["task_id"],
            agent=data["agent"],
            request=data["request"],
            run_at=datetime.fromisoformat(data["run_at"]),
            priority=data.get("priority", "normal")
        )
        task.status = data.get("status", "pending")
        return task


class TaskScheduler:
    """Schedule tasks for delayed execution."""
    
    def __init__(self, schedule_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/scheduled.json"):
        self.schedule_file = schedule_file
        self._ensure_file()
        self.tasks = self._load()
    
    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
        if not os.path.exists(self.schedule_file):
            with open(self.schedule_file, "w") as f:
                json.dump([], f)
    
    def _load(self) -> List[Dict]:
        with open(self.schedule_file, "r") as f:
            return json.load(f)
    
    def _save(self):
        with open(self.schedule_file, "w") as f:
            json.dump(self.tasks, f, indent=2)
    
    def schedule(
        self,
        agent: str,
        request: str,
        run_at: datetime,
        priority: str = "normal"
    ) -> str:
        """Schedule a task for later execution."""
        task_id = str(uuid.uuid4())
        
        task = ScheduledTask(
            task_id=task_id,
            agent=agent,
            request=request,
            run_at=run_at,
            priority=priority
        )
        
        self.tasks.append(task.to_dict())
        self._save()
        
        return task_id
    
    def get_pending(self) -> List[Dict]:
        """Get all pending scheduled tasks."""
        return [t for t in self.tasks if t["status"] == "pending"]
    
    def get_ready(self) -> List[Dict]:
        """Get tasks that are ready to run (past their scheduled time)."""
        now = datetime.utcnow()
        ready = []
        
        for task in self.tasks:
            if task["status"] == "pending":
                run_at = datetime.fromisoformat(task["run_at"])
                if run_at <= now:
                    ready.append(task)
        
        return ready
    
    def get_ready_tasks(self) -> List[Dict]:
        """Alias for get_ready."""
        return self.get_ready()
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        for task in self.tasks:
            if task["task_id"] == task_id:
                task["status"] = "cancelled"
                self._save()
                return True
        return False
    
    def complete(self, task_id: str):
        """Mark a task as completed."""
        for task in self.tasks:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                self._save()
                return True
        return False
    
    def get_by_agent(self, agent: str) -> List[Dict]:
        """Get scheduled tasks for a specific agent."""
        return [t for t in self.tasks if t["agent"] == agent]


if __name__ == "__main__":
    import sys
    
    scheduler = TaskScheduler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            pending = scheduler.get_pending()
            print(f"Pending: {len(pending)}")
            for t in pending[:5]:
                print(f"  {t['task_id'][:8]} | {t['agent']} | {t['request'][:30]}")
        
        elif sys.argv[1] == "ready":
            ready = scheduler.get_ready()
            print(f"Ready: {len(ready)}")
            for t in ready:
                print(f"  {t['task_id'][:8]} | {t['agent']} | {t['request'][:30]}")
    else:
        print("Usage: scheduler.py <list|ready>")