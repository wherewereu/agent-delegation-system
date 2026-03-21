"""
Event Types and Handlers
Define event types and their handlers
"""
from enum import Enum
from typing import Dict, Any, Callable, Optional


class EventType(Enum):
    """All event types in the system."""
    DELEGATION = "delegation"
    COMPLETION = "completion"
    FAILURE = "failure"
    HEALTH_CHANGE = "health_change"
    CIRCUIT_OPEN = "circuit_open"
    CIRCUIT_CLOSE = "circuit_close"
    METRICS_UPDATE = "metrics_update"
    SCHEDULED_TASK_READY = "scheduled_task_ready"
    LEARNING_UPDATE = "learning_update"


class EventHandler:
    """Base class for event handlers."""
    
    def __init__(self, name: str):
        self.name = name
    
    def handle(self, event: Dict[str, Any]) -> Optional[Dict]:
        """Handle event. Returns optional response."""
        raise NotImplementedError


class DelegationEventHandler(EventHandler):
    """Handle delegation events."""
    
    def handle(self, event: Dict[str, Any]) -> Dict:
        return {
            "type": "delegation_acknowledged",
            "task_id": event.get("task_id"),
            "agent": event.get("agent")
        }


class CompletionEventHandler(EventHandler):
    """Handle completion events."""
    
    def handle(self, event: Dict[str, Any]) -> Dict:
        return {
            "type": "completion_recorded",
            "task_id": event.get("task_id"),
            "result": event.get("result")
        }


class FailureEventHandler(EventHandler):
    """Handle failure events."""
    
    def __init__(self, name: str = "failure_handler"):
        super().__init__(name)
        self.failure_count = 0
    
    def handle(self, event: Dict[str, Any]) -> Dict:
        self.failure_count += 1
        
        return {
            "type": "failure_recorded",
            "task_id": event.get("task_id"),
            "error": event.get("error"),
            "total_failures": self.failure_count
        }


# Registry of event handlers
EVENT_HANDLERS: Dict[EventType, EventHandler] = {
    EventType.DELEGATION: DelegationEventHandler("delegation"),
    EventType.COMPLETION: CompletionEventHandler("completion"),
    EventType.FAILURE: FailureEventHandler("failure"),
}


def get_handler(event_type: EventType) -> Optional[EventHandler]:
    """Get handler for event type."""
    return EVENT_HANDLERS.get(event_type)


def register_handler(event_type: EventType, handler: EventHandler):
    """Register a custom event handler."""
    EVENT_HANDLERS[event_type] = handler


if __name__ == "__main__":
    print("Event handlers registered:")
    for et in EventType:
        handler = get_handler(et)
        print(f"  {et.value}: {handler.name if handler else 'none'}")