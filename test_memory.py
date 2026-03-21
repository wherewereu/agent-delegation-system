"""
Test: Agent Memory Persistence
Red first - tests for daily memory files per agent
"""
import pytest
import os
import json
from datetime import datetime
from agent_memory import AgentMemory, MEMORY_DIR


TEST_MEMORY_DIR = "/tmp/test_agent_memory"


class TestAgentMemory:
    """Test agent memory file management."""

    def setup_method(self):
        # Clean up test memory dir
        import shutil
        if os.path.exists(TEST_MEMORY_DIR):
            shutil.rmtree(TEST_MEMORY_DIR)

    def teardown_method(self):
        import shutil
        if os.path.exists(TEST_MEMORY_DIR):
            shutil.rmtree(TEST_MEMORY_DIR)

    def test_memory_dir_created(self):
        """Memory directory should be created"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        assert os.path.exists(TEST_MEMORY_DIR)

    def test_daily_log_created(self):
        """Daily log file should be created"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        # Log something to ensure file is created
        mem.log("test", "initial entry")
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(TEST_MEMORY_DIR, "scout", f"{today}.md")
        assert os.path.exists(log_path)

    def test_log_activity(self):
        """Should be able to log activity"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem.log("research", "researched Bitcoin history")
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(TEST_MEMORY_DIR, "scout", f"{today}.md")
        
        with open(log_path, "r") as f:
            content = f.read()
        
        assert "researched Bitcoin history" in content

    def test_log_multiple_activities(self):
        """Should log multiple activities with timestamps"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem.log("research", "task 1")
        mem.log("research", "task 2")
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(TEST_MEMORY_DIR, "scout", f"{today}.md")
        
        with open(log_path, "r") as f:
            content = f.read()
        
        assert "task 1" in content
        assert "task 2" in content

    def test_log_includes_timestamp(self):
        """Log entry should include timestamp"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem.log("research", "test task")
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(TEST_MEMORY_DIR, "scout", f"{today}.md")
        
        with open(log_path, "r") as f:
            content = f.read()
        
        # Should have timestamp-like format (HH:MM)
        assert "**" in content and "|" in content  # Markdown bold timestamp

    def test_different_agents_different_files(self):
        """Each agent should have separate memory file"""
        mem1 = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem2 = AgentMemory("link", memory_dir=TEST_MEMORY_DIR)
        
        mem1.log("research", "scout task")
        mem2.log("comms", "link task")
        
        today = datetime.now().strftime("%Y-%m-%d")
        scout_path = os.path.join(TEST_MEMORY_DIR, "scout", f"{today}.md")
        link_path = os.path.join(TEST_MEMORY_DIR, "link", f"{today}.md")
        
        with open(scout_path, "r") as f:
            assert "scout task" in f.read()
        
        with open(link_path, "r") as f:
            assert "link task" in f.read()

    def test_get_recent_activities(self):
        """Should be able to get recent activities"""
        mem = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem.log("research", "task 1")
        mem.log("research", "task 2")
        mem.log("research", "task 3")
        
        activities = mem.get_recent(limit=2)
        
        # Should get last 2 activities
        assert len(activities) == 2

    def test_memory_persists_across_instances(self):
        """Memory should persist when creating new instance"""
        mem1 = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        mem1.log("research", "persisted task")
        
        # Create new instance
        mem2 = AgentMemory("scout", memory_dir=TEST_MEMORY_DIR)
        activities = mem2.get_recent(limit=5)
        
        assert any("persisted task" in a for a in activities)