"""
Test: Intent Classification
Red first - these tests should FAIL until we implement classify()
"""
import pytest
from classify import classify, Agent


class TestIntentClassification:
    """Test cases for intent classification logic."""

    # === RESEARCH / SCOUT ===
    def test_research_keyword_returns_scout(self):
        result = classify("research the history of bitcoin")
        assert result.agent == Agent.SCOUT
        assert result.confidence >= 0.7

    def test_search_keyword_returns_scout(self):
        result = classify("search for best pizza near me")
        assert result.agent == Agent.SCOUT
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_what_is_returns_scout(self):
        result = classify("what is machine learning")
        assert result.agent == Agent.SCOUT

    def test_who_is_returns_scout(self):
        result = classify("who is the president of france")
        assert result.agent == Agent.SCOUT

    # === COMMUNICATIONS / LINK ===
    def test_email_keyword_returns_link(self):
        result = classify("send an email to john")
        assert result.agent == Agent.LINK
        assert result.confidence >= 0.7

    def test_message_keyword_returns_link(self):
        result = classify("message Justine on telegram")
        assert result.agent == Agent.LINK

    def test_post_keyword_returns_link(self):
        result = classify("post this to linkedin")
        assert result.agent == Agent.LINK

    def test_gmail_keyword_returns_link(self):
        result = classify("check my gmail inbox")
        assert result.agent == Agent.LINK

    # === PROCUREMENT / CART ===
    def test_order_keyword_returns_cart(self):
        result = classify("order more coffee beans")
        assert result.agent == Agent.CART
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_buy_keyword_returns_cart(self):
        result = classify("buy groceries from instacart")
        assert result.agent == Agent.CART

    def test_shop_keyword_returns_cart(self):
        result = classify("shop for new headphones")
        assert result.agent == Agent.CART

    def test_amazon_keyword_returns_cart(self):
        result = classify("order from amazon")
        assert result.agent == Agent.CART

    # === CALENDAR / CLOCK ===
    def test_calendar_keyword_returns_clock(self):
        result = classify("add to calendar")
        assert result.agent == Agent.CLOCK
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_schedule_keyword_returns_clock(self):
        result = classify("schedule a meeting for 3pm")
        assert result.agent == Agent.CLOCK

    def test_remind_keyword_returns_clock(self):
        result = classify("remind me to call mom at 5pm")
        assert result.agent == Agent.CLOCK
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_event_keyword_returns_clock(self):
        result = classify("create event for tomorrow")
        assert result.agent == Agent.CLOCK

    # === HEALTH / VITAL ===
    def test_water_keyword_returns_vital(self):
        result = classify("track my water intake")
        assert result.agent == Agent.VITAL
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_health_keyword_returns_vital(self):
        result = classify("log my health data")
        assert result.agent == Agent.VITAL

    def test_sleep_keyword_returns_vital(self):
        result = classify("how did i sleep last night")
        assert result.agent == Agent.VITAL

    def test_diet_keyword_returns_vital(self):
        result = classify("track my diet calories")
        assert result.agent == Agent.VITAL

    # === CODE / FORGE ===
    def test_code_keyword_returns_forge(self):
        result = classify("write some code for me")
        assert result.agent == Agent.FORGE
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_script_keyword_returns_forge(self):
        result = classify("create a backup script")
        assert result.agent == Agent.FORGE

    def test_build_keyword_returns_forge(self):
        result = classify("build a new feature")
        assert result.agent == Agent.FORGE

    def test_fix_keyword_returns_forge(self):
        result = classify("fix the bug in login")
        assert result.agent == Agent.FORGE

    # === REVIEW / JUDGE ===
    def test_review_keyword_returns_judge(self):
        result = classify("review this code")
        assert result.agent == Agent.JUDGE
        assert result.confidence >= 0.4  # 1 keyword = medium

    def test_verify_keyword_returns_judge(self):
        result = classify("verify the solution")
        assert result.agent == Agent.JUDGE

    def test_audit_keyword_returns_judge(self):
        result = classify("audit the security")
        assert result.agent == Agent.JUDGE

    # === CONFIDENCE THRESHOLDS ===
    def test_high_confidence_auto_delegate(self):
        """Score >= 2 keywords = high confidence (>=0.7)"""
        result = classify("order coffee beans from amazon")
        assert result.action == "auto_delegate"
        assert result.confidence >= 0.7

    def test_medium_confidence_delegate_with_monitoring(self):
        """Score == 1 keyword = medium confidence"""
        result = classify("buy milk")
        assert result.action == "delegate_with_monitoring"
        assert 0.4 <= result.confidence < 0.7

    def test_low_confidence_escalate(self):
        """No keywords matched = escalate to orchestrator"""
        result = classify("hello there")
        assert result.action == "escalate"
        assert result.confidence < 0.4

    # === EDGE CASES ===
    def test_empty_string_escalates(self):
        result = classify("")
        assert result.action == "escalate"

    def test_case_insensitive(self):
        result = classify("SEND EMAIL TO JOHN")
        assert result.agent == Agent.LINK

    def test_punctuation_handled(self):
        result = classify("remind me to call mom!!!")
        assert result.agent == Agent.CLOCK

    def test_compound_request_takes_highest(self):
        """If multiple agents match, take highest score"""
        result = classify("email mom and schedule meeting")
        # Both Link and Clock could match - need disambiguation
        # For now, take highest score
        assert result.agent in [Agent.LINK, Agent.CLOCK]

    def test_unknown_request_escalates(self):
        result = classify("do something cool")
        assert result.action == "escalate"