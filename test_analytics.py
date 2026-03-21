"""
Test: Analytics and Load Balancing
Red first - tests for analytics and scaling
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from analytics import Analytics, DelegationReport


TEST_ANALYTICS_FILE = "/tmp/test_analytics.json"


class TestAnalytics:
    """Test analytics and reporting."""

    def setup_method(self):
        if os.path.exists(TEST_ANALYTICS_FILE):
            os.remove(TEST_ANALYTICS_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_ANALYTICS_FILE):
            os.remove(TEST_ANALYTICS_FILE)

    def test_generate_report(self):
        """Should generate delegation report"""
        analytics = Analytics(analytics_file=TEST_ANALYTICS_FILE)
        
        # Record some delegations
        analytics.record_delegation("scout", "success", 100)
        analytics.record_delegation("scout", "success", 150)
        analytics.record_delegation("link", "failed", 200)
        
        report = analytics.generate_report()
        
        assert report["total_delegations"] == 3
        assert report["scout"]["success_count"] == 2

    def test_hourly_breakdown(self):
        """Should provide hourly breakdown"""
        analytics = Analytics(analytics_file=TEST_ANALYTICS_FILE)
        
        # Record with timestamps
        now = datetime.utcnow()
        
        analytics.record_delegation("scout", "success", 100)
        
        # Add old entry
        old_time = (now - timedelta(hours=2)).isoformat()
        analytics.record_delegation("scout", "success", 100, timestamp=old_time)
        
        hourly = analytics.get_hourly_stats(hours=1)
        
        # Should only have 1 delegation in last hour
        assert hourly[0]["delegations"] == 1

    def test_agent_performance_ranking(self):
        """Should rank agents by performance"""
        analytics = Analytics(analytics_file=TEST_ANALYTICS_FILE)
        
        # Scout: 5 successes
        for _ in range(5):
            analytics.record_delegation("scout", "success", 100)
        
        # Link: 2 failures
        for _ in range(2):
            analytics.record_delegation("link", "failed", 100)
        
        rankings = analytics.get_agent_rankings()
        
        # Scout should be ranked higher
        scout_rank = next(r for r in rankings if r["agent"] == "scout")
        link_rank = next(r for r in rankings if r["agent"] == "link")
        
        assert scout_rank["rank"] < link_rank["rank"]

    def test_export_json(self):
        """Should export analytics as JSON"""
        analytics = Analytics(analytics_file=TEST_ANALYTICS_FILE)
        
        analytics.record_delegation("scout", "success", 100)
        
        export = analytics.export_json()
        
        parsed = json.loads(export)
        assert "total_delegations" in parsed


class TestLoadBalancing:
    """Test load balancing across agent instances."""

    def test_distribute_tasks_evenly(self):
        """Should distribute tasks evenly across instances"""
        from load_balancer import LoadBalancer
        
        lb = LoadBalancer()
        
        # Register 3 instances of scout
        lb.register_instance("scout", "instance-1")
        lb.register_instance("scout", "instance-2")
        lb.register_instance("scout", "instance-3")
        
        # Get task assignments
        assignments = []
        for _ in range(6):
            instance = lb.get_next_instance("scout")
            assignments.append(instance)
        
        # Should cycle through instances
        assert len(set(assignments)) > 1

    def test_remove_unhealthy_instance(self):
        """Should remove unhealthy instance from pool"""
        from load_balancer import LoadBalancer
        
        lb = LoadBalancer()
        
        lb.register_instance("scout", "instance-1")
        lb.register_instance("scout", "instance-2")
        
        # Mark instance-1 as unhealthy
        lb.mark_unhealthy("scout", "instance-1")
        
        # Get next - should only return instance-2
        instance = lb.get_next_instance("scout")
        
        assert instance == "instance-2"

    def test_scale_up_instances(self):
        """Should add more instances when needed"""
        from load_balancer import LoadBalancer
        
        lb = LoadBalancer()
        
        # Register 1 instance
        lb.register_instance("scout", "instance-1")
        
        # Scale up to 3
        lb.scale("scout", 3)
        
        # Check instances
        instances = lb.get_instances("scout")
        
        assert len(instances) >= 3