"""
Delegation Router
Orchestrates classification + state management + Hydra messaging
"""
import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
import requests

from classify import classify, Agent
from state import AgentState, TaskStatus
from logging_config import logger, LogLevel
from discord_notifier import notifier


@dataclass
class DelegationResult:
    """Result of a delegation attempt"""
    task_id: str
    agent: str
    action: str
    success: bool
    priority: str = "normal"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: str = ""
    error: Optional[str] = None


class DelegationError(Exception):
    """Raised when delegation fails"""
    pass


# Hydra mesh relay endpoint
HYDRA_ENDPOINT = "http://192.168.0.247:8500/messages/send"

# State file location
STATE_FILE = "/Users/soup/.openclaw/workspace/delegation/memory/agent-state.json"

# Retry config
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1


def calculate_backoff(attempt: int) -> int:
    """Calculate exponential backoff delay"""
    return RETRY_BASE_DELAY * (2 ** attempt)


def send_to_hydra(message: Dict) -> Dict:
    """Send message to Hydra mesh relay"""
    try:
        response = requests.post(
            HYDRA_ENDPOINT,
            json=message,
            timeout=5
        )
        if response.status_code == 200:
            return {"status": "delivered", "response": response.json()}
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}


class DelegationRouter:
    """
    Main router - combines classification, state, and messaging.
    This is Milo.
    """

    def __init__(self, state_file: Optional[str] = None):
        self.state = AgentState()

        # Try to load existing state
        self.state_file = state_file or STATE_FILE
        try:
            self.state = AgentState.load(self.state_file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Start fresh

    def save_state(self):
        """Persist state to disk"""
        import os
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.state.save(self.state_file)

    def delegate(self, request: str, priority: str = "normal") -> DelegationResult:
        """
        Main entry point: classify request, check availability, delegate.

        Args:
            request: Raw user request string
            priority: "urgent", "normal", or "low"

        Returns:
            DelegationResult with outcome
        """
        task_id = str(uuid.uuid4())

        # Step 1: Classify intent
        classification = classify(request)
        
        # Log classification
        logger.log_classification(
            request=request,
            agent=classification.agent.value,
            confidence=classification.confidence,
            action=classification.action
        )

        agent_name = classification.agent.value
        action = classification.action

        # Step 2: Check availability or use fallback
        if action == "escalate":
            return DelegationResult(
                task_id=task_id,
                agent="milo",
                action="escalate",
                success=False,
                priority=priority,
                notes="Intent classification confidence too low",
                error="No matching keywords"
            )

        # Check if agent is available
        if not self.state.is_available(agent_name):
            fallback = self.state.get_fallback(agent_name)
            agent_name = fallback
            notes = f"Primary agent busy, fell back to {fallback}"
        else:
            notes = f"Delegated to {agent_name} (confidence: {classification.confidence})"

        # Step 3: Add task to state
        self.state.add_task(agent_name, task_id, priority=priority)
        self.save_state()
        
        # Log delegation
        logger.log_delegation(
            task_id=task_id,
            agent=agent_name,
            request=request,
            confidence=classification.confidence,
            priority=priority
        )
        
        # Send Discord notification (non-blocking)
        try:
            notifier.send_delegation(task_id, agent_name, request, priority)
        except Exception:
            pass  # Non-blocking

        # Step 4: Send to Hydra with retry logic
        message = {
            "sender": "milo",
            "recipient": agent_name,
            "content": request,
            "task_type": agent_name,
            "task_id": task_id,
            "priority": priority,
            "metadata": {
                "user_request": request,
                "callback_channel": "telegram"
            }
        }
        
        # Retry logic
        import time
        last_error = None
        for attempt in range(MAX_RETRIES):
            hydra_response = send_to_hydra(message)
            
            if hydra_response.get("status") == "delivered":
                break  # Success
            else:
                last_error = hydra_response.get("error", "Unknown error")
                if attempt < MAX_RETRIES - 1:
                    backoff = calculate_backoff(attempt)
                    time.sleep(backoff)
        
        if hydra_response.get("status") != "delivered":
            # Failed after retries - add to dead-letter
            from state import dead_letter_queue_add
            dead_letter_queue_add(
                task_id=task_id,
                agent=agent_name,
                error=last_error or "Max retries exceeded",
                original_request=request,
                priority=priority
            )
            
            # Log failure
            logger.log_failure(
                task_id=task_id,
                agent=agent_name,
                error=last_error or "Max retries exceeded",
                retry_count=MAX_RETRIES
            )
            
            return DelegationResult(
                task_id=task_id,
                agent=agent_name,
                action="failed",
                success=False,
                priority=priority,
                notes=f"Failed after {MAX_RETRIES} attempts",
                error=last_error
            )

        # Log successful delegation
        logger.log(
            level=LogLevel.INFO,
            message="Task delegated successfully",
            task_id=task_id,
            agent=agent_name,
            event="success"
        )

        return DelegationResult(
            task_id=task_id,
            agent=agent_name,
            action=action,
            success=True,
            priority=priority,
            notes=notes
        )

    def complete(self, task_id: str) -> bool:
        """Mark a task as completed"""
        # Find which agent has this task
        task = self.state.get_task_status(task_id)
        if not task:
            return False
        
        self.state.complete_task(task["agent"], task_id)
        self.save_state()
        
        # Log completion
        logger.log_completion(
            task_id=task_id,
            agent=task["agent"],
            result="success"
        )
        
        # Discord notification
        try:
            notifier.send_completion(task_id, task["agent"], "success")
        except Exception:
            pass
        
        return True

    def fail(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        task = self.state.get_task_status(task_id)
        if not task:
            return False

        self.state.fail_task(task["agent"], task_id, error)
        self.save_state()
        
        # Log failure
        logger.log_failure(
            task_id=task_id,
            agent=task["agent"],
            error=error
        )
        
        # Discord notification
        try:
            notifier.send_failure(task_id, task["agent"], error)
        except Exception:
            pass
        
        return True

    def get_pending(self) -> List[Dict]:
        """Get all pending delegations"""
        return self.state.get_pending_tasks()

    def get_agent_load(self, agent: str) -> Dict:
        """Get load info for an agent"""
        return self.state.get_agent_load(agent)

    def status(self) -> Dict:
        """Get overall router status"""
        return {
            "agents": {
                agent: self.state.get_agent_load(agent)
                for agent in ["scout", "link", "cart", "clock", "vital", "forge", "judge"]
            },
            "pending_tasks": len(self.get_pending())
        }


# CLI interface
if __name__ == "__main__":
    import sys
    import os

    router = DelegationRouter()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "delegate":
            request = " ".join(sys.argv[2:])
            result = router.delegate(request)
            print(f"Task ID: {result.task_id}")
            print(f"Agent: {result.agent}")
            print(f"Action: {result.action}")
            print(f"Success: {result.success}")
            print(f"Notes: {result.notes}")

        elif cmd == "status":
            status = router.status()
            print(json.dumps(status, indent=2))

        elif cmd == "pending":
            pending = router.get_pending()
            print(json.dumps(pending, indent=2))

        elif cmd == "complete":
            task_id = sys.argv[2]
            router.complete(task_id)
            print(f"Completed {task_id}")

        elif cmd == "classify":
            request = " ".join(sys.argv[2:])
            result = classify(request)
            print(f"Agent: {result.agent.value}")
            print(f"Confidence: {result.confidence}")
            print(f"Action: {result.action}")
    else:
        print("Usage: python router.py <command> [args]")
        print("Commands: delegate, status, pending, complete, classify")