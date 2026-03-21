"""
Circuit Breaker
Circuit breaker pattern implementation for agent reliability
"""
from datetime import datetime
from typing import Optional


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    States:
    - closed: Normal operation, requests allowed
    - open: Too many failures, requests blocked
    - half-open: Testing if recovery is possible
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    def record_failure(self):
        """Record a failure and potentially open the circuit"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def record_success(self):
        """Record a success and reset the circuit"""
        self.failures = 0
        self.state = "closed"
    
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)"""
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
        """Check if a request can be executed"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            return False
        elif self.state == "half-open":
            return True
        return False
    
    def get_state(self) -> str:
        """Get current circuit state"""
        return self.state
    
    def reset(self):
        """Manually reset the circuit"""
        self.failures = 0
        self.state = "closed"
        self.last_failure_time = None