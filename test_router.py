"""
Test: Delegation Router
Red first - tests for the full routing pipeline
"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock
from router import DelegationRouter, DelegationResult, DelegationError
from classify import Agent
from state import AgentState


TEST_STATE_FILE = "/tmp/test_router_state.json"


class TestDelegationRouter:
    """Test the full delegation flow."""

    def setup_method(self):
        """Setup before each test"""
        # Clean state file before each test
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)
        
        # Mock Hydra to avoid actual network calls
        self.mock_hydra = patch('router.send_to_hydra').start()
        self.mock_hydra.return_value = {"status": "delivered"}

    def teardown_method(self):
        """Cleanup after each test"""
        patch.stopall()
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)

    def test_classify_and_delegate_research(self):
        """Should classify and delegate research request to Scout"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research the history of bitcoin")
        
        assert result.agent == "scout"
        assert result.action == "auto_delegate"
        assert result.success is True

    def test_classify_and_delegate_email(self):
        """Should classify and delegate email request to Link"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("send email to john")
        
        assert result.agent == "link"
        assert result.success is True

    def test_classify_and_delegate_calendar(self):
        """Should classify and delegate calendar request to Clock"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("remind me to call mom at 5pm")
        
        assert result.agent == "clock"
        assert result.success is True

    def test_classify_and_delegate_shopping(self):
        """Should classify and delegate shopping request to Cart"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("order coffee beans from amazon")
        
        assert result.agent == "cart"
        assert result.success is True

    def test_classify_and_delegate_code(self):
        """Should classify and delegate code request to Forge"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("write a backup script")
        
        assert result.agent == "forge"
        assert result.success is True

    def test_delegate_when_agent_busy_uses_fallback(self):
        """Should fallback when primary agent is busy"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        
        # Fill Forge to max (2)
        router.state.add_task("forge", "task-1")
        router.state.add_task("forge", "task-2")
        
        # Now delegate code task - should fallback to judge
        result = router.delegate("write some code")
        
        assert result.agent == "judge"  # Fallback
        assert "fallback" in result.notes.lower() or "busy" in result.notes.lower()

    def test_escalate_when_unknown_intent(self):
        """Should escalate when intent is unknown"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("hello there how are you")
        
        assert result.agent == "milo"
        assert result.action == "escalate"
        assert result.success is False

    def test_delegate_with_priority_urgent(self):
        """Should respect urgent priority"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("URGENT: fix the login bug now", priority="urgent")
        
        assert result.priority == "urgent"
        assert result.task_id is not None

    def test_delegate_with_priority_low(self):
        """Should respect low priority"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("sometime later fix this", priority="low")
        
        assert result.priority == "low"

    def test_task_id_is_uuid(self):
        """Task ID should be a valid UUID"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research something")
        
        # UUID format: 8-4-4-4-12 hex
        assert len(result.task_id) == 36
        assert result.task_id.count("-") == 4

    def test_delegate_creates_task_in_state(self):
        """Delegation should create task in state"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research bitcoin")
        
        status = router.state.get_task_status(result.task_id)
        assert status is not None
        assert status["agent"] == "scout"
        assert status["status"] == "pending"

    def test_complete_task_via_router(self):
        """Should be able to complete task through router"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research bitcoin")
        
        router.complete(result.task_id)
        
        status = router.state.get_task_status(result.task_id)
        assert status["status"] == "completed"

    def test_fail_task_via_router(self):
        """Should be able to fail task through router"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research bitcoin")
        
        router.fail(result.task_id, "timeout")
        
        status = router.state.get_task_status(result.task_id)
        assert status["status"] == "failed"
        assert status["error"] == "timeout"

    def test_get_pending_delegations(self):
        """Should list all pending delegations"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        router.delegate("research bitcoin")
        router.delegate("send email", priority="urgent")
        router.delegate("order coffee")
        
        pending = router.get_pending()
        
        assert len(pending) >= 3

    def test_delegation_includes_timestamp(self):
        """Delegation result should include timestamp"""
        router = DelegationRouter(state_file=TEST_STATE_FILE)
        result = router.delegate("research something")
        
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO format


class TestDelegationResult:
    """Test the result dataclass."""

    def test_result_has_required_fields(self):
        """Result should have all required fields"""
        result = DelegationResult(
            task_id="test-123",
            agent="scout",
            action="auto_delegate",
            success=True,
            priority="normal",
            timestamp="2026-03-21T12:00:00",
            notes=""
        )
        
        assert result.task_id == "test-123"
        assert result.agent == "scout"
        assert result.action == "auto_delegate"
        assert result.success is True