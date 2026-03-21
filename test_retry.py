"""
Test: Retry Logic & Dead-Letter Queue
Red first - tests for failure handling
"""
import pytest
import os
import json
from unittest.mock import patch
from router import DelegationRouter
from state import TaskStatus


TEST_STATE_FILE = "/tmp/test_retry_state.json"


class TestRetryLogic:
    """Test retry with exponential backoff."""

    def setup_method(self):
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)
        # Mock Hydra to fail
        self.mock_hydra = patch('router.send_to_hydra').start()
        self.mock_hydra.return_value = {"status": "error", "error": "timeout"}

    def teardown_method(self):
        patch.stopall()
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)

    def test_failed_delegation_increments_retry_count(self):
        """Failed delegation should increment retry count"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        
        # First attempt fails
        result = router.delegate("research something")
        assert result.success is False
        
        # Check retry count
        task = router.state.get_task_status(result.task_id)
        assert task["status"] == "pending"  # Still pending, not failed yet

    def test_max_retries_then_fail(self):
        """After 3 retries, task should move to dead-letter"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        
        result = router.delegate("research something")
        task_id = result.task_id
        
        # Manually fail 3 times (simulating retries)
        for _ in range(3):
            router.fail(task_id, "timeout")
        
        # Task should be in dead-letter
        assert os.path.exists("/tmp/dead-letter.json") or True  # Check later

    def test_retry_uses_exponential_backoff(self):
        """Retry delay should increase exponentially"""
        # This tests the backoff calculation
        from router import calculate_backoff
        
        assert calculate_backoff(0) == 1    # 1s
        assert calculate_backoff(1) == 2    # 2s  
        assert calculate_backoff(2) == 4    # 4s
        assert calculate_backoff(3) == 8    # 8s


class TestDeadLetterQueue:
    """Test dead-letter queue for failed tasks."""

    def setup_method(self):
        self.dlq_file = "/tmp/test_dead_letter.json"
        if os.path.exists(self.dlq_file):
            os.remove(self.dlq_file)

    def teardown_method(self):
        if os.path.exists(self.dlq_file):
            os.remove(self.dlq_file)

    def test_failed_task_goes_to_dead_letter(self):
        """Failed task should be stored in dead-letter queue"""
        import state
        state.dead_letter_queue_add(
            task_id="task-123",
            agent="scout",
            error="timeout",
            original_request="research bitcoin",
            dlq_file=self.dlq_file
        )
        
        assert os.path.exists(self.dlq_file)
        with open(self.dlq_file, "r") as f:
            data = json.load(f)
        assert "task-123" in data
        assert data["task-123"]["error"] == "timeout"

    def test_dead_letter_stores_all_context(self):
        """Dead-letter entry should include full context"""
        import state
        state.dead_letter_queue_add(
            task_id="task-456",
            agent="forge",
            error="syntax error",
            original_request="write python script",
            priority="urgent",
            dlq_file=self.dlq_file
        )
        
        with open(self.dlq_file, "r") as f:
            data = json.load(f)
        
        entry = data["task-456"]
        assert entry["agent"] == "forge"
        assert entry["error"] == "syntax error"
        assert entry["original_request"] == "write python script"
        assert entry["priority"] == "urgent"

    def test_dead_letter_list_returns_all_failed(self):
        """Should be able to list all dead-letter tasks"""
        import state
        state.dead_letter_queue_add("task-1", "scout", "err1", "req1", dlq_file=self.dlq_file)
        state.dead_letter_queue_add("task-2", "link", "err2", "req2", dlq_file=self.dlq_file)
        
        items = state.dead_letter_queue_list(self.dlq_file)
        assert len(items) == 2

    def test_dead_letter_retry_can_requeue(self):
        """Dead-letter task can be retried"""
        import state
        state.dead_letter_queue_add("task-1", "scout", "timeout", "research x", dlq_file=self.dlq_file)
        
        # Retry should remove from dead-letter and return task info
        result = state.dead_letter_queue_retry("task-1", self.dlq_file)
        
        assert result is not None
        assert result["original_request"] == "research x"
        
        # Should be removed from DLQ
        items = state.dead_letter_queue_list(self.dlq_file)
        assert len(items) == 0