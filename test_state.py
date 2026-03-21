"""
Test: Agent State Management
Red first - tests for availability, max concurrent, queuing
"""
import pytest
import os
import json
from state import AgentState, TaskStatus


TEST_STATE_FILE = "/tmp/test_agent_state.json"


class TestAgentState:
    """Test agent availability and state tracking."""

    def setup_method(self):
        """Clean up before each test"""
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)

    def teardown_method(self):
        """Clean up after each test"""
        if os.path.exists(TEST_STATE_FILE):
            os.remove(TEST_STATE_FILE)

    def test_agent_within_limit_is_available(self):
        """Agent under max concurrent should be available"""
        state = AgentState()
        # Scout has max 3
        assert state.is_available("scout") is True

    def test_agent_at_limit_is_unavailable(self):
        """Agent at max concurrent should be unavailable"""
        state = AgentState()
        # Fill Scout to max (3)
        state.add_task("scout", "task-1")
        state.add_task("scout", "task-2")
        state.add_task("scout", "task-3")
        
        assert state.is_available("scout") is False

    def test_agent_over_limit_is_unavailable(self):
        """Agent over max should still be unavailable"""
        state = AgentState()
        state.add_task("scout", "task-1")
        state.add_task("scout", "task-2")
        state.add_task("scout", "task-3")
        state.add_task("scout", "task-4")  # Over limit
        
        assert state.is_available("scout") is False

    def test_task_completion_frees_slot(self):
        """Completing a task frees up a slot"""
        state = AgentState()
        # Add 3 tasks to fill Scout (max 3)
        state.add_task("scout", "task-1")
        state.add_task("scout", "task-2")
        state.add_task("scout", "task-3")
        
        # At max capacity
        assert state.is_available("scout") is False
        
        # Complete one, frees a slot
        state.complete_task("scout", "task-1")
        
        assert state.is_available("scout") is True

    def test_get_available_slots(self):
        """Should return number of available slots"""
        state = AgentState()
        state.add_task("scout", "task-1")
        
        # Scout max is 3, has 1, so 2 available
        assert state.get_available_slots("scout") == 2

    def test_unknown_agent_is_unavailable(self):
        """Unknown agent should return unavailable"""
        state = AgentState()
        assert state.is_available("unknown-agent") is False

    def test_task_status_tracking(self):
        """Task status should be trackable"""
        state = AgentState()
        state.add_task("scout", "task-1", priority="urgent")
        
        status = state.get_task_status("task-1")
        assert status is not None
        assert status["agent"] == "scout"
        assert status["status"] == "pending"
        assert status["priority"] == "urgent"

    def test_task_completion_updates_status(self):
        """Completing task should update status"""
        state = AgentState()
        state.add_task("scout", "task-1")
        state.complete_task("scout", "task-1")
        
        status = state.get_task_status("task-1")
        assert status["status"] == "completed"

    def test_task_failure_marks_failed(self):
        """Failed task should be marked as failed"""
        state = AgentState()
        state.add_task("scout", "task-1")
        state.fail_task("scout", "task-1", "timeout")
        
        status = state.get_task_status("task-1")
        assert status["status"] == "failed"
        assert status["error"] == "timeout"

    def test_pending_tasks_returns_all_pending(self):
        """Should return all pending tasks"""
        state = AgentState()
        state.add_task("scout", "task-1")
        state.add_task("scout", "task-2")
        state.add_task("link", "task-3")
        
        pending = state.get_pending_tasks()
        
        assert len(pending) == 3

    def test_pending_tasks_respects_priority(self):
        """Higher priority tasks should come first"""
        state = AgentState()
        state.add_task("scout", "task-1", priority="low")
        state.add_task("scout", "task-2", priority="urgent")
        state.add_task("scout", "task-3", priority="normal")
        
        pending = state.get_pending_tasks()
        
        # Urgent should be first
        assert pending[0]["priority"] == "urgent"

    def test_load_state_from_file(self):
        """Should load state from JSON file"""
        # Create a state file in OUR format
        test_data = {
            "current_tasks": {
                "scout": ["task-1"],
                "link": []
            },
            "tasks": {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "scout",
                    "description": "",
                    "priority": "normal",
                    "status": "pending",
                    "created_at": "2026-03-21T00:00:00",
                    "completed_at": None,
                    "error": None
                }
            }
        }
        with open(TEST_STATE_FILE, "w") as f:
            json.dump(test_data, f)
        
        state = AgentState.load(TEST_STATE_FILE)
        
        assert state.current_tasks.get("scout") == ["task-1"]
        assert state.current_tasks.get("link") == []

    def test_save_state_to_file(self):
        """Should save state to JSON file"""
        state = AgentState()
        state.add_task("scout", "task-1")
        
        state.save(TEST_STATE_FILE)
        
        with open(TEST_STATE_FILE, "r") as f:
            data = json.load(f)
        
        # Check nested path
        assert "scout" in data["current_tasks"]
        assert "task-1" in data["current_tasks"]["scout"]


class TestFallbackRouting:
    """Test fallback routing when primary agent unavailable."""

    def test_forge_fallbacks_to_judge(self):
        """Code tasks fall back to review when busy"""
        state = AgentState()
        # Fill Forge to max (2)
        state.add_task("forge", "task-1")
        state.add_task("forge", "task-2")
        
        # Check fallback
        fallback = state.get_fallback("forge")
        assert fallback == "judge"

    def test_specialists_fallback_to_milo(self):
        """Most agents fall back to Milo when busy"""
        state = AgentState()
        
        assert state.get_fallback("scout") == "milo"
        assert state.get_fallback("link") == "milo"
        assert state.get_fallback("cart") == "milo"
        assert state.get_fallback("clock") == "milo"
        assert state.get_fallback("vital") == "milo"