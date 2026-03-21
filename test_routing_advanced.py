"""
Test: Natural Language Routing Rules
Red first - tests for config-based routing
"""
import pytest
import os
import json
from routing_config import RoutingRuleEngine, RoutingRule


TEST_RULES_FILE = "/tmp/test_routing_rules.json"


class TestRoutingRules:
    """Test natural language routing configuration."""

    def setup_method(self):
        if os.path.exists(TEST_RULES_FILE):
            os.remove(TEST_RULES_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_RULES_FILE):
            os.remove(TEST_RULES_FILE)

    def test_add_rule(self):
        """Should add a routing rule"""
        engine = RoutingRuleEngine(rules_file=TEST_RULES_FILE)
        
        rule = engine.add_rule(
            condition="contains keyword bitcoin",
            agent="scout",
            priority=10
        )
        
        assert rule is not None
        assert rule["agent"] == "scout"

    def test_match_rule(self):
        """Should match request against rules"""
        engine = RoutingRuleEngine(rules_file=TEST_RULES_FILE)
        
        engine.add_rule("contains keyword crypto", "scout", 10)
        engine.add_rule("contains keyword email", "link", 10)
        
        match = engine.match("learn about crypto")
        
        assert match == "scout"

    def test_priority_ordering(self):
        """Higher priority rules should match first"""
        engine = RoutingRuleEngine(rules_file=TEST_RULES_FILE)
        
        engine.add_rule("contains keyword test", "scout", 1)
        engine.add_rule("contains keyword test", "judge", 10)
        
        match = engine.match("run test suite")
        
        assert match == "judge"

    def test_no_match_returns_none(self):
        """No matching rule should return None"""
        engine = RoutingRuleEngine(rules_file=TEST_RULES_FILE)
        
        engine.add_rule("contains keyword crypto", "scout", 10)
        
        match = engine.match("hello world")
        
        assert match is None

    def test_rule_conditions(self):
        """Test different rule conditions"""
        engine = RoutingRuleEngine(rules_file=TEST_RULES_FILE)
        
        # starts with
        engine.add_rule("starts with order", "cart", 10)
        assert engine.match("order coffee") == "cart"
        
        # ends with  
        engine.add_rule("ends with bug", "forge", 10)
        assert engine.match("please fix this bug") == "forge"
        
        # contains
        engine.add_rule("contains keyword email", "link", 10)
        assert engine.match("send an email please") == "link"


class TestABTesting:
    """Test A/B testing for routing."""

    def test_create_experiment(self):
        """Should create A/B experiment"""
        from ab_testing import ABExperiment, ABTester
        
        experiment = ABExperiment(
            name="routing_test",
            variants=["scout", "judge"]
        )
        
        assert experiment.name == "routing_test"
        assert len(experiment.variants) == 2

    def test_assign_variant(self):
        """Should assign variant to user"""
        from ab_testing import ABExperiment
        
        exp = ABExperiment("test", ["a", "b"])
        
        # Deterministic assignment based on user_id
        v1 = exp.get_variant("user-123")
        v2 = exp.get_variant("user-456")
        
        assert v1 in ["a", "b"]
        assert v2 in ["a", "b"]

    def test_track_conversion(self):
        """Should track conversion rate"""
        from ab_testing import ABExperiment
        
        # Create fresh experiment file
        test_file = "/tmp/test_ab.json"
        if os.path.exists(test_file):
            os.remove(test_file)
        
        experiment = ABExperiment("test", ["control", "treatment"], experiment_file=test_file)
        
        # Record conversions
        experiment.record_conversion("user-1", "control")
        experiment.record_conversion("user-2", "control")
        experiment.record_conversion("user-3", "treatment")
        
        stats = experiment.get_stats()
        
        assert stats["control"]["conversions"] == 2
        assert stats["treatment"]["conversions"] == 1
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_winner_determination(self):
        """Should determine winning variant"""
        test_file = "/tmp/test_ab2.json"
        if os.path.exists(test_file):
            os.remove(test_file)
        
        from ab_testing import ABExperiment
        
        exp = ABExperiment("test", ["a", "b"], experiment_file=test_file)
        
        # A performs better
        for _ in range(10):
            exp.record_conversion(f"user-{_}", "a")
        for _ in range(5):
            exp.record_conversion(f"user-b{_}", "b")
        
        winner = exp.get_winner()
        
        assert winner == "a"
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)