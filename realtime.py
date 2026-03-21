"""
Real-time Event System
WebSocket server and event broadcasting
"""
import json
from typing import Dict, List, Callable, Any
from enum import Enum


class EventType(Enum):
    """Types of events in the delegation system."""
    DELEGATION = "delegation"
    COMPLETION = "completion"
    FAILURE = "failure"
    METRICS = "metrics"
    HEALTH = "health"


class EventEmitter:
    """Simple event emitter for delegation events."""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[Callable]] = {}
    
    def on(self, event_type: EventType, handler: Callable):
        """Register event handler."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit(self, event_type: EventType, data: Any):
        """Emit event to all handlers."""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Event handler error: {e}")


class EventBroadcaster:
    """Broadcast events to WebSocket clients."""
    
    def __init__(self):
        self.clients: List[Any] = []
    
    def add_client(self, client):
        """Add a WebSocket client."""
        self.clients.append(client)
    
    def remove_client(self, client):
        """Remove a WebSocket client."""
        if client in self.clients:
            self.clients.remove(client)
    
    def broadcast(self, event: Dict):
        """Broadcast event to all clients."""
        message = json.dumps(event)
        
        for client in self.clients:
            try:
                client.send(message)
            except Exception as e:
                print(f"Broadcast error: {e}")
                self.remove_client(client)
    
    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)


class WebSocketServer:
    """WebSocket server for real-time updates."""
    
    def __init__(self, port: int = 8765, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.broadcaster = EventBroadcaster()
        self.emitter = EventEmitter()
    
    def get_broadcaster(self) -> EventBroadcaster:
        """Get the event broadcaster."""
        return self.broadcaster
    
    def get_emitter(self) -> EventEmitter:
        """Get the event emitter."""
        return self.emitter
    
    def emit_delegation(self, task_id: str, agent: str, request: str):
        """Emit delegation event."""
        event = {
            "type": "delegation",
            "task_id": task_id,
            "agent": agent,
            "request": request
        }
        
        self.emitter.emit(EventType.DELEGATION, event)
        self.broadcaster.broadcast(event)
    
    def emit_completion(self, task_id: str, result: str):
        """Emit completion event."""
        event = {
            "type": "completion",
            "task_id": task_id,
            "result": result
        }
        
        self.emitter.emit(EventType.COMPLETION, event)
        self.broadcaster.broadcast(event)
    
    def emit_failure(self, task_id: str, error: str):
        """Emit failure event."""
        event = {
            "type": "failure",
            "task_id": task_id,
            "error": error
        }
        
        self.emitter.emit(EventType.FAILURE, event)
        self.broadcaster.broadcast(event)


# Global instance
realtime = WebSocketServer()


if __name__ == "__main__":
    import sys
    
    rt = WebSocketServer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print(f"Clients: {rt.broadcaster.get_client_count()}")
    else:
        print("WebSocket server ready")
        print(f"Port: {rt.port}, Host: {rt.host}")