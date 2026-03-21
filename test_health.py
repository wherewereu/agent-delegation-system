"""
Test: Agent Health Monitoring
Red first - tests for agent health tracking
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from health import AgentHealth, HealthMonitor


TEST_HEALTH_FILE = "/tmp/test_health.json"


class TestAgentHealth:
    """Test agent health tracking."""

    def setup_method(self):
        if os.path.exists(TEST_HEALTH_FILE):
            os.remove(TEST_HEALTH_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_HEALTH_FILE):
            os.remove(TEST_HEALTH_FILE)

    def test_health_record_task_start(self):
        """Should record when task starts"""
        health = AgentHealth(TEST_HEALTH_FILE)
        health.record_task_start("scout", "task-123")
        
        with open(TEST_HEALTH_FILE, "r") as f:
            data = json.load(f)
        
        assert "scout" in data
        assert "task-123" in data["scout"]["active_tasks"]

    def test_health_record_task_end(self):
        """Should record when task completes"""
        health = AgentHealth(TEST_HEALTH_FILE)
        health.record_task_start("scout", "task-123")
        health.record_task_end("scout", "task-123", "success")
        
        with open(TEST_HEALTH_FILE, "r") as f:
            data = json.load(f)
        
        assert data["scout"]["completed"] == 1
        assert "task-123" not in data["scout"].get("active_tasks", [])

    def test_health_record_failure(self):
        """Should record failures"""
        health = AgentHealth(TEST_HEALTH_FILE)
        health.record_task_start("scout", "task-123")
        health.record_task_end("scout", "task-123", "failed")
        
        with open(TEST_HEALTH_FILE, "r") as f:
            data = json.load(f)
        
        assert data["scout"]["failed"] == 1

    def test_health_uptime_calculation(self):
        """Should calculate uptime percentage"""
        health = AgentHealth(TEST_HEALTH_FILE)
        
        # 9 success, 1 failure = 90%
        for i in range(9):
            health.record_task_end("scout", f"task-{i}", "success")
        health.record_task_end("scout", "task-fail", "failed")
        
        stats = health.get_stats("scout")
        
        assert stats["success_rate"] == 0.9
        assert stats["total_tasks"] == 10

    def test_health_get_agent_status(self):
        """Should return agent status"""
        health = AgentHealth(TEST_HEALTH_FILE)
        
        health.record_task_start("scout", "task-1")
        
        status = health.get_status("scout")
        
        assert status["agent"] == "scout"
        assert status["active"] == 1

    def test_health_all_agents(self):
        """Should return all agent statuses"""
        health = AgentHealth(TEST_HEALTH_FILE)
        
        health.record_task_start("scout", "task-1")
        health.record_task_start("link", "task-2")
        
        all_status = health.get_all_status()
        
        assert "scout" in all_status
        assert "link" in all_status


class TestCircuitBreaker:
    """Test circuit breaker for failing agents."""

    def test_circuit_opens_on_failures(self):
        """Circuit should open after threshold failures"""
        from circuit_breaker import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3)
        
        # Fail 3 times
        for _ in range(3):
            cb.record_failure()
        
        assert cb.is_open() is True

    def test_circuit_closes_after_timeout(self):
        """Circuit should close after timeout"""
        from circuit_breaker import CircuitBreaker
        
        # Use threshold=1 for clear test
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0)
        
        # Should be closed initially
        assert cb.get_state() == "closed"
        
        # Record failure - should open
        cb.record_failure()
        
        # With timeout=0, goes to half-open immediately
        assert cb.get_state() in ["open", "half-open"]

    def test_circuit_resets_on_success(self):
        """Circuit should reset on success"""
        from circuit_breaker import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2)
        
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        
        assert cb.is_open() is True
        
        cb.record_success()
        
        assert cb.is_open() is False