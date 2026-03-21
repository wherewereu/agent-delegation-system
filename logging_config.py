"""
Structured Logging for Delegation System
JSON-formatted logs for observability
"""
import json
import os
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class DelegationLogger:
    """Structured JSON logger for delegation events."""
    
    def __init__(self, log_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/delegation.log"):
        self.log_file = log_file
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)
    
    def log(
        self,
        level: LogLevel,
        message: str,
        agent: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs
    ):
        """Log a structured message"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "message": message,
        }
        
        if agent:
            entry["agent"] = agent
        if task_id:
            entry["task_id"] = task_id
        
        # Add any additional fields
        entry.update(kwargs)
        
        # Write to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_delegation(
        self,
        task_id: str,
        agent: str,
        request: str,
        confidence: float,
        priority: str = "normal"
    ):
        """Log a delegation event"""
        self.log(
            level=LogLevel.INFO,
            message="Task delegated",
            event="delegation",
            task_id=task_id,
            agent=agent,
            request=request[:100],  # Truncate for log
            confidence=confidence,
            priority=priority
        )
    
    def log_completion(
        self,
        task_id: str,
        agent: str,
        result: str = "success",
        duration_ms: Optional[int] = None
    ):
        """Log task completion"""
        self.log(
            level=LogLevel.INFO,
            message="Task completed",
            event="completion",
            task_id=task_id,
            agent=agent,
            result=result,
            duration_ms=duration_ms
        )
    
    def log_failure(
        self,
        task_id: str,
        agent: str,
        error: str,
        retry_count: int = 0
    ):
        """Log task failure"""
        self.log(
            level=LogLevel.ERROR,
            message="Task failed",
            event="failure",
            task_id=task_id,
            agent=agent,
            error=error,
            retry_count=retry_count
        )
    
    def log_metrics(
        self,
        agent: str,
        total_tasks: int,
        successful: int,
        failed: int,
        avg_latency_ms: int
    ):
        """Log periodic metrics"""
        success_rate = successful / total_tasks if total_tasks > 0 else 0
        
        self.log(
            level=LogLevel.INFO,
            message="Agent metrics",
            event="metrics",
            agent=agent,
            total_tasks=total_tasks,
            successful=successful,
            failed=failed,
            success_rate=round(success_rate, 2),
            avg_latency_ms=avg_latency_ms
        )
    
    def log_classification(
        self,
        request: str,
        agent: str,
        confidence: float,
        action: str
    ):
        """Log intent classification"""
        self.log(
            level=LogLevel.DEBUG,
            message="Intent classified",
            event="classification",
            request=request[:50],
            agent=agent,
            confidence=confidence,
            action=action
        )


# Global logger instance
logger = DelegationLogger()


if __name__ == "__main__":
    import sys
    
    logger = DelegationLogger()
    
    if len(sys.argv) > 1:
        level = sys.argv[1].upper()
        message = " ".join(sys.argv[2:])
        
        logger.log(LogLevel[level], message)
        print(f"Logged: {level} - {message}")
    else:
        # Demo
        logger.log_delegation("task-1", "scout", "research bitcoin", 0.8)
        logger.log_completion("task-1", "scout", "success", 150)
        print("Demo logs written")