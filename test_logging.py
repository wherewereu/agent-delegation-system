"""
Test: Structured Logging
Red first - tests for JSON logging
"""
import pytest
import os
import json
from unittest.mock import patch, mock_open
from logging_config import DelegationLogger, LogLevel


TEST_LOG_FILE = "/tmp/test_delegation.log"


class TestStructuredLogging:
    """Test structured JSON logging."""

    def setup_method(self):
        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def test_log_entry_is_valid_json(self):
        """Log entries should be valid JSON"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        logger.log(LogLevel.INFO, "test_message", agent="scout")
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "message" in parsed

    def test_log_includes_all_fields(self):
        """Log entry should include timestamp, level, message, agent, task_id"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        logger.log(LogLevel.INFO, "task delegated", agent="scout", task_id="abc-123")
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert parsed["agent"] == "scout"
        assert parsed["task_id"] == "abc-123"
        assert parsed["message"] == "task delegated"

    def test_log_levels_work(self):
        """All log levels should be recorded"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        
        logger.log(LogLevel.DEBUG, "debug msg")
        logger.log(LogLevel.INFO, "info msg")
        logger.log(LogLevel.WARN, "warning msg")
        logger.log(LogLevel.ERROR, "error msg")
        
        with open(TEST_LOG_FILE, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 4
        assert "DEBUG" in lines[0]
        assert "INFO" in lines[1]
        assert "WARN" in lines[2]
        assert "ERROR" in lines[3]

    def test_delegation_event_logged(self):
        """Delegation events should be logged with context"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        
        logger.log_delegation(
            task_id="task-001",
            agent="scout",
            request="research bitcoin",
            confidence=0.8
        )
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert parsed["event"] == "delegation"
        assert parsed["task_id"] == "task-001"
        assert parsed["confidence"] == 0.8

    def test_completion_event_logged(self):
        """Task completion should be logged"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        
        logger.log_completion(task_id="task-001", agent="scout", result="success")
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert parsed["event"] == "completion"
        assert parsed["result"] == "success"

    def test_failure_event_logged(self):
        """Task failure should be logged with error"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        
        logger.log_failure(task_id="task-001", agent="scout", error="timeout")
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert parsed["event"] == "failure"
        assert parsed["error"] == "timeout"

    def test_metrics_logged(self):
        """Metrics should be logged periodically"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        
        logger.log_metrics(
            agent="scout",
            total_tasks=10,
            successful=8,
            failed=2,
            avg_latency_ms=150
        )
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        assert parsed["event"] == "metrics"
        assert parsed["total_tasks"] == 10
        assert parsed["success_rate"] == 0.8

    def test_timestamps_are_iso_format(self):
        """Timestamps should be ISO format"""
        logger = DelegationLogger(log_file=TEST_LOG_FILE)
        logger.log(LogLevel.INFO, "test")
        
        with open(TEST_LOG_FILE, "r") as f:
            line = f.readline()
        
        parsed = json.loads(line)
        # ISO format has T and Z
        assert "T" in parsed["timestamp"]
        assert "Z" in parsed["timestamp"] or "+" in parsed["timestamp"]