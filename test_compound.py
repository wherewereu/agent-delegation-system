"""
Test: Compound Request Chains
Red first - tests for handling multi-agent tasks
"""
import pytest
from classify import classify_compound, Agent


class TestCompoundRequests:
    """Test handling of requests that need multiple agents."""

    def test_single_agent_simple(self):
        """Simple request maps to one agent"""
        result = classify_compound("remind me to call mom")
        assert len(result) == 1
        assert result[0]["agent"] == "clock"

    def test_two_agents_email_and_calendar(self):
        """Request mentions email AND calendar"""
        result = classify_compound("email john and schedule meeting")
        assert len(result) == 2
        agents = [r["agent"] for r in result]
        assert "link" in agents
        assert "clock" in agents

    def test_three_agents_all_keywords(self):
        """Request triggers three agents"""
        result = classify_compound("email boss, schedule meeting, and order supplies")
        assert len(result) == 3
        agents = [r["agent"] for r in result]
        assert "link" in agents
        assert "clock" in agents
        assert "cart" in agents

    def test_chain_execution_order(self):
        """Agents should be ordered correctly (Link before Clock for email+calendar)"""
        result = classify_compound("email mom and schedule dinner")
        # Link should come before Clock (email then calendar)
        agents = [r["agent"] for r in result]
        assert agents.index("link") < agents.index("clock")

    def test_compound_returns_confidence_per_agent(self):
        """Each agent should have its own confidence score"""
        result = classify_compound("email and calendar")
        for r in result:
            assert "confidence" in r
            assert r["confidence"] > 0

    def test_empty_request_returns_empty(self):
        """Empty request returns empty list"""
        result = classify_compound("")
        assert len(result) == 0

    def test_single_word_triggers_single(self):
        """Single keyword triggers single agent"""
        result = classify_compound("order coffee")
        assert len(result) == 1

    def test_compound_with_research_and_code(self):
        """Research and code together"""
        result = classify_compound("research how to build an API and write the code")
        assert len(result) == 2
        agents = [r["agent"] for r in result]
        assert "scout" in agents
        assert "forge" in agents