"""
Standardized Error Codes
Define error codes for inter-agent communication
"""
from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """Standard error codes for the delegation system."""
    
    # General errors
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    
    # Agent errors
    AGENT_UNAVAILABLE = "AGENT_UNAVAILABLE"
    AGENT_BUSY = "AGENT_BUSY"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    
    # Task errors
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_EXPIRED = "TASK_EXPIRED"
    TASK_CANCELLED = "TASK_CANCELLED"
    
    # Communication errors
    MESSAGE_SEND_FAILED = "MESSAGE_SEND_FAILED"
    MESSAGE_ENCRYPTION_FAILED = "MESSAGE_ENCRYPTION_FAILED"
    HYDRRA_UNAVAILABLE = "HYDRA_UNAVAILABLE"
    
    # Classification errors
    CLASSIFICATION_FAILED = "CLASSIFICATION_FAILED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    AMBIGUOUS_REQUEST = "AMBIGUOUS_REQUEST"
    
    # System errors
    STATE_CORRUPTED = "STATE_CORRUPTED"
    MEMORY_ERROR = "MEMORY_ERROR"
    DISK_FULL = "DISK_FULL"


ERROR_MESSAGES = {
    ErrorCode.UNKNOWN: "An unknown error occurred",
    ErrorCode.TIMEOUT: "The request timed out",
    ErrorCode.AGENT_UNAVAILABLE: "The requested agent is unavailable",
    ErrorCode.AGENT_BUSY: "The agent is currently busy",
    ErrorCode.AGENT_NOT_FOUND: "The specified agent was not found",
    ErrorCode.CIRCUIT_OPEN: "Circuit breaker is open for this agent",
    ErrorCode.TASK_NOT_FOUND: "The specified task was not found",
    ErrorCode.TASK_EXPIRED: "The task has expired",
    ErrorCode.TASK_CANCELLED: "The task was cancelled",
    ErrorCode.MESSAGE_SEND_FAILED: "Failed to send message to agent",
    ErrorCode.MESSAGE_ENCRYPTION_FAILED: "Failed to encrypt message",
    ErrorCode.HYDRRA_UNAVAILABLE: "The Hydra mesh relay is unavailable",
    ErrorCode.CLASSIFICATION_FAILED: "Failed to classify the request",
    ErrorCode.LOW_CONFIDENCE: "Classification confidence too low",
    ErrorCode.AMBIGUOUS_REQUEST: "Request is ambiguous, multiple agents could handle it",
    ErrorCode.STATE_CORRUPTED: "Agent state file is corrupted",
    ErrorCode.MEMORY_ERROR: "Failed to access agent memory",
    ErrorCode.DISK_FULL: "Disk is full, cannot write state",
}


def get_error_message(code: ErrorCode) -> str:
    """Get human-readable error message."""
    return ERROR_MESSAGES.get(code, "Unknown error")


class DelegationError(Exception):
    """Base exception for delegation errors."""
    
    def __init__(self, code: ErrorCode, message: str = None):
        self.code = code
        self.message = message or get_error_message(code)
        super().__init__(self.message)
    
    def to_dict(self):
        return {
            "code": self.code.value,
            "message": self.message
        }


class AgentUnavailableError(DelegationError):
    """Raised when agent is unavailable."""
    
    def __init__(self, agent: str):
        super().__init__(ErrorCode.AGENT_UNAVAILABLE, f"Agent {agent} is unavailable")


class ClassificationError(DelegationError):
    """Raised when classification fails."""
    
    def __init__(self, reason: str):
        super().__init__(ErrorCode.CLASSIFICATION_FAILED, reason)


class CircuitBreakerError(DelegationError):
    """Raised when circuit breaker is open."""
    
    def __init__(self, agent: str):
        super().__init__(ErrorCode.CIRCUIT_OPEN, f"Circuit breaker open for {agent}")


if __name__ == "__main__":
    print("Error Codes:")
    for code in ErrorCode:
        print(f"  {code.value}: {get_error_message(code)}")