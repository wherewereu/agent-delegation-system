"""
Test: Scheduled Tasks
Red first - tests for delayed/queued task execution
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from scheduler import TaskScheduler, ScheduledTask


TEST_SCHEDULE_FILE = "/tmp/test_schedule.json"


class TestScheduledTasks:
    """Test scheduled task functionality."""

    def setup_method(self):
        if os.path.exists(TEST_SCHEDULE_FILE):
            os.remove(TEST_SCHEDULE_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_SCHEDULE_FILE):
            os.remove(TEST_SCHEDULE_FILE)

    def test_schedule_task(self):
        """Should be able to schedule a task for later"""
        scheduler = TaskScheduler(schedule_file=TEST_SCHEDULE_FILE)
        
        # Schedule for 1 minute from now
        run_at = datetime.utcnow() + timedelta(minutes=1)
        
        task_id = scheduler.schedule(
            agent="scout",
            request="research bitcoin",
            run_at=run_at
        )
        
        assert task_id is not None
        assert len(task_id) > 0

    def test_get_pending_scheduled(self):
        """Should return pending scheduled tasks"""
        scheduler = TaskScheduler(schedule_file=TEST_SCHEDULE_FILE)
        
        # Schedule for now
        run_at = datetime.utcnow() - timedelta(minutes=1)  # in the past = ready
        
        scheduler.schedule("scout", "task1", run_at)
        scheduler.schedule("link", "task2", run_at)
        
        pending = scheduler.get_pending()
        
        assert len(pending) == 2

    def test_cancel_scheduled_task(self):
        """Should be able to cancel a scheduled task"""
        scheduler = TaskScheduler(schedule_file=TEST_SCHEDULE_FILE)
        
        run_at = datetime.utcnow() + timedelta(hours=1)
        task_id = scheduler.schedule("scout", "task1", run_at)
        
        result = scheduler.cancel(task_id)
        
        assert result is True

    def test_task_runs_after_delay(self):
        """Tasks should be executable after their scheduled time"""
        scheduler = TaskScheduler(schedule_file=TEST_SCHEDULE_FILE)
        
        # Schedule for past (should be ready)
        run_at = datetime.utcnow() - timedelta(minutes=1)
        task_id = scheduler.schedule("scout", "delayed research", run_at)
        
        ready = scheduler.get_ready_tasks()
        
        ready_ids = [t["task_id"] for t in ready]
        assert task_id in ready_ids


class TestLearningPatterns:
    """Test learning from delegation patterns."""

    def test_store_delegation_result(self):
        """Should store delegation result for learning"""
        from learning import LearningEngine
        
        engine = LearningEngine()
        
        engine.record(
            request="research bitcoin",
            agent="scout",
            success=True,
            latency_ms=150
        )
        
        # Check it was stored
        history = engine.get_history()
        
        assert len(history) > 0

    def test_get_best_agent_for_request(self):
        """Should learn which agent works best for request type"""
        from learning import LearningEngine
        
        engine = LearningEngine()
        
        # Record multiple successes for scout on "research" requests
        for _ in range(5):
            engine.record("research x", "scout", True, 100)
        
        # Record failures for link on same
        for _ in range(3):
            engine.record("research x", "link", False, 200)
        
        best = engine.get_best_agent("research x")
        
        assert best == "scout"

    def test_improve_confidence_based_on_history(self):
        """Should adjust confidence based on past success"""
        from learning import LearningEngine
        
        engine = LearningEngine()
        
        # Good track record with scout
        for _ in range(10):
            engine.record("bitcoin history", "scout", True, 100)
        
        confidence = engine.get_adjusted_confidence("scout", "bitcoin history", 0.7)
        
        # Should be higher than base 0.7
        assert confidence > 0.7