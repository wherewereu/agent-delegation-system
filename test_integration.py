"""
Test: Integration Tests
Red first - tests for full delegation flow
"""
import pytest
import os
import json
from unittest.mock import patch


class TestIntegrationFlow:
    """Test full integration flows."""

    def setup_method(self):
        # Clean state
        state_file = "/tmp/test_integration_state.json"
        if os.path.exists(state_file):
            os.remove(state_file)

    def teardown_method(self):
        state_file = "/tmp/test_integration_state.json"
        if os.path.exists(state_file):
            os.remove(state_file)

    def test_full_delegation_flow(self):
        """Test complete delegation: classify → delegate → complete"""
        from router import DelegationRouter
        
        with patch('router.send_to_hydra') as mock_hydra:
            mock_hydra.return_value = {"status": "delivered"}
            
            router = DelegationRouter(state_file="/tmp/test_integration_state.json")
            
            # Delegate a task
            result = router.delegate("research bitcoin")
            
            # Verify
            assert result.success is True
            assert result.agent == "scout"
            assert result.task_id is not None
            
            # Verify task is tracked
            status = router.state.get_task_status(result.task_id)
            assert status is not None
            assert status["agent"] == "scout"
            
            # Complete the task
            router.complete(result.task_id)
            
            # Verify completion
            status = router.state.get_task_status(result.task_id)
            assert status["status"] == "completed"

    def test_fallback_when_agent_busy(self):
        """Test fallback to alternate agent when primary busy"""
        from router import DelegationRouter
        
        with patch('router.send_to_hydra') as mock_hydra:
            mock_hydra.return_value = {"status": "delivered"}
            
            router = DelegationRouter(state_file="/tmp/test_integration_state.json")
            
            # Fill forge to max capacity (2)
            router.state.add_task("forge", "task-1")
            router.state.add_task("forge", "task-2")
            
            # Now delegate code task
            result = router.delegate("write some code")
            
            # Should fallback to judge
            assert result.agent == "judge"
            assert "fell back" in result.notes.lower() or "busy" in result.notes.lower()

    def test_escalate_on_low_confidence(self):
        """Test escalation when confidence is too low"""
        from router import DelegationRouter
        
        with patch('router.send_to_hydra') as mock_hydra:
            mock_hydra.return_value = {"status": "delivered"}
            
            router = DelegationRouter(state_file="/tmp/test_integration_state.json")
            
            # Use vague request
            result = router.delegate("hello there")
            
            # Should escalate to milo
            assert result.agent == "milo"
            assert result.action == "escalate"

    def test_priority_respected(self):
        """Test that priority is tracked"""
        from router import DelegationRouter
        
        with patch('router.send_to_hydra') as mock_hydra:
            mock_hydra.return_value = {"status": "delivered"}
            
            router = DelegationRouter(state_file="/tmp/test_integration_state.json")
            
            result = router.delegate("research bitcoin", priority="urgent")
            
            assert result.priority == "urgent"

    def test_compound_delegation(self):
        """Test compound request delegates to multiple agents"""
        from classify import classify_compound
        
        result = classify_compound("email mom and schedule meeting")
        
        assert len(result) >= 2
        agents = [r["agent"] for r in result]
        assert "link" in agents
        assert "clock" in agents


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_hydra_failure_triggers_retry(self):
        """Test that Hydra failure triggers retry"""
        from router import DelegationRouter
        
        call_count = 0
        
        def mock_hydra(*args):
            nonlocal call_count
            call_count += 1
            return {"status": "error", "error": "timeout"}
        
        with patch('router.send_to_hydra', side_effect=mock_hydra):
            router = DelegationRouter(state_file="/tmp/test_integration_state.json")
            
            result = router.delegate("research bitcoin")
            
            # Should have retried
            assert call_count >= 1

    def test_task_not_found_returns_false(self):
        """Test that completing unknown task returns False"""
        from router import DelegationRouter
        
        router = DelegationRouter(state_file="/tmp/test_integration_state.json")
        
        result = router.complete("nonexistent-task")
        
        assert result is False