"""
Discord Notifier for Delegation System
Posts delegation events to Discord channel via webhook
"""
import os
import json
import requests
from typing import Optional
from datetime import datetime


class DiscordNotifier:
    """Send delegation events to Discord."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
    
    def _post(self, payload: dict) -> bool:
        """Send message to Discord webhook"""
        if not self.webhook_url:
            print("Discord webhook not configured - skipping notification")
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Discord webhook error: {e}")
            return False
    
    def send_delegation(self, task_id: str, agent: str, request: str, priority: str = "normal") -> bool:
        """Send delegation notification"""
        emoji = {
            "scout": "🔍",
            "link": "📧",
            "cart": "🛒",
            "clock": "🕐",
            "vital": "❤️",
            "forge": "⚒️",
            "judge": "⚖️",
            "milo": "🎯"
        }
        
        embed = {
            "title": f"{emoji.get(agent, '🎯')} Task Delegated",
            "color": 5763714,  # Green
            "fields": [
                {"name": "Agent", "value": agent, "inline": True},
                {"name": "Priority", "value": priority, "inline": True},
                {"name": "Task ID", "value": f"`{task_id[:8]}...`", "inline": True},
                {"name": "Request", "value": request[:100]}
            ],
            "footer": {"text": "Flume Delegation System"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._post({"embeds": [embed]})
    
    def send_completion(self, task_id: str, agent: str, result: str = "success") -> bool:
        """Send completion notification"""
        emoji = "✅" if result == "success" else "❌"
        
        embed = {
            "title": f"{emoji} Task {result.title()}",
            "color": 5763714 if result == "success" else 15548964,  # Green or Red
            "fields": [
                {"name": "Agent", "value": agent, "inline": True},
                {"name": "Task ID", "value": f"`{task_id[:8]}...`", "inline": True}
            ],
            "footer": {"text": "Flume Delegation System"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._post({"embeds": [embed]})
    
    def send_failure(self, task_id: str, agent: str, error: str, retry_count: int = 0) -> bool:
        """Send failure notification"""
        embed = {
            "title": "❌ Task Failed",
            "color": 15548974,  # Red
            "fields": [
                {"name": "Agent", "value": agent, "inline": True},
                {"name": "Retries", "value": str(retry_count), "inline": True},
                {"name": "Task ID", "value": f"`{task_id[:8]}...`", "inline": True},
                {"name": "Error", "value": error[:100]}
            ],
            "footer": {"text": "Flume Delegation System"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._post({"embeds": [embed]})
    
    def send_metrics(self, total: int, success_rate: float, by_agent: dict) -> bool:
        """Send periodic metrics summary"""
        agent_lines = []
        for agent, data in by_agent.items():
            rate = int(data.get("success_rate", 0) * 100)
            agent_lines.append(f"  {agent}: {data['total']} tasks, {rate}% success")
        
        embed = {
            "title": "📊 Delegation Metrics",
            "color": 7506394,  # Blue
            "fields": [
                {"name": "Total Tasks", "value": str(total), "inline": True},
                {"name": "Success Rate", "value": f"{int(success_rate * 100)}%", "inline": True},
                {"name": "By Agent", "value": "\n".join(agent_lines) if agent_lines else "No data"}
            ],
            "footer": {"text": "Flume Delegation System"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._post({"embeds": [embed]})


# Global notifier
notifier = DiscordNotifier()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: discord_notifier.py <event> <args>")
        print("Events: delegation, completion, failure, metrics")
        sys.exit(1)
    
    event = sys.argv[1]
    
    if event == "delegation":
        task_id = sys.argv[2]
        agent = sys.argv[3]
        request = sys.argv[4] if len(sys.argv) > 4 else ""
        priority = sys.argv[5] if len(sys.argv) > 5 else "normal"
        notifier.send_delegation(task_id, agent, request, priority)
    
    elif event == "completion":
        task_id = sys.argv[2]
        agent = sys.argv[3]
        notifier.send_completion(task_id, agent)
    
    elif event == "failure":
        task_id = sys.argv[2]
        agent = sys.argv[3]
        error = sys.argv[4] if len(sys.argv) > 4 else "unknown"
        notifier.send_failure(task_id, agent, error)