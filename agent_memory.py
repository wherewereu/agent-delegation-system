"""
Agent Memory Management
Daily memory files for each agent - tracks activities and context
"""
import os
from datetime import datetime
from typing import List, Optional

# Default memory directory
MEMORY_DIR = "/Users/soup/.openclaw/workspace/delegation/memory"


class AgentMemory:
    """Manages daily memory files for an agent."""
    
    def __init__(self, agent_name: str, memory_dir: str = MEMORY_DIR):
        self.agent_name = agent_name
        self.memory_dir = memory_dir
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create agent memory directory if needed"""
        agent_dir = os.path.join(self.memory_dir, self.agent_name)
        os.makedirs(agent_dir, exist_ok=True)
    
    def _get_today_file(self) -> str:
        """Get today's memory file path"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.memory_dir, self.agent_name, f"{today}.md")
    
    def log(self, activity_type: str, description: str):
        """Log an activity to today's memory file"""
        file_path = self._get_today_file()
        
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format: HH:MM | type | description
        entry = f"- **{timestamp}** | {activity_type} | {description}\n"
        
        with open(file_path, "a") as f:
            f.write(entry)
    
    def get_recent(self, limit: int = 10) -> List[str]:
        """Get recent activities from today's log"""
        file_path = self._get_today_file()
        
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, "r") as f:
            lines = f.readlines()
        
        # Return last 'limit' entries
        return [line.strip() for line in lines[-limit:] if line.strip()]
    
    def get_today_summary(self) -> str:
        """Get all of today's activities as a string"""
        file_path = self._get_today_file()
        
        if not os.path.exists(file_path):
            return "No activities logged today."
        
        with open(file_path, "r") as f:
            return f.read()
    
    def get_stats(self) -> dict:
        """Get memory statistics for this agent"""
        agent_dir = os.path.join(self.memory_dir, self.agent_name)
        
        if not os.path.exists(agent_dir):
            return {"days_active": 0, "total_entries": 0}
        
        days = [f for f in os.listdir(agent_dir) if f.endswith(".md")]
        
        total_entries = 0
        for day_file in days:
            with open(os.path.join(agent_dir, day_file), "r") as f:
                total_entries += len(f.readlines())
        
        return {
            "agent": self.agent_name,
            "days_active": len(days),
            "total_entries": total_entries
        }


def log_delegation(agent: str, task: str, result: str):
    """Quick helper to log a delegation"""
    mem = AgentMemory(agent)
    mem.log("delegation", f"{task} → {result}")


def log_completion(agent: str, task: str):
    """Quick helper to log task completion"""
    mem = AgentMemory(agent)
    mem.log("completion", task)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: agent_memory.py <agent> <message>")
        print("Example: agent_memory.py scout 'researched bitcoin'")
        sys.exit(1)
    
    agent = sys.argv[1]
    message = " ".join(sys.argv[2:])
    
    mem = AgentMemory(agent)
    mem.log("manual", message)
    print(f"Logged to {agent}: {message}")