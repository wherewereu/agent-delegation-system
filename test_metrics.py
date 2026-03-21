"""
Test: Metrics Dashboard
Red first - tests for metrics calculation and display
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from metrics import MetricsCollector, MetricsDashboard


TEST_LOG_FILE = "/tmp/test_metrics.log"


class TestMetricsCollector:
    """Test metrics calculation from logs."""

    def setup_method(self):
        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def teardown_method(self):
        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def test_calculate_total_delegations(self):
        """Should count total delegations"""
        # Write sample logs
        with open(TEST_LOG_FILE, "w") as f:
            f.write('{"event": "delegation", "agent": "scout"}\n')
            f.write('{"event": "delegation", "agent": "link"}\n')
            f.write('{"event": "delegation", "agent": "scout"}\n')
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        metrics = collector.get_overall_metrics()
        
        assert metrics["total_delegations"] == 3

    def test_calculate_success_rate(self):
        """Should calculate success rate"""
        with open(TEST_LOG_FILE, "w") as f:
            # Include delegation events so total is counted
            f.write('{"event": "delegation", "agent": "scout"}\n')
            f.write('{"event": "delegation", "agent": "link"}\n')
            f.write('{"event": "delegation", "agent": "forge"}\n')
            f.write('{"event": "delegation", "agent": "clock"}\n')
            f.write('{"event": "completion", "result": "success"}\n')
            f.write('{"event": "completion", "result": "success"}\n')
            f.write('{"event": "completion", "result": "success"}\n')
            f.write('{"event": "failure", "error": "timeout"}\n')
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        metrics = collector.get_overall_metrics()
        
        # 4 delegations, 3 completed, 1 failed
        assert metrics["total_delegations"] == 4
        assert metrics["completed"] == 3
        assert metrics["failed"] == 1
        assert metrics["success_rate"] == 0.75

    def test_per_agent_stats(self):
        """Should calculate per-agent statistics"""
        with open(TEST_LOG_FILE, "w") as f:
            f.write('{"event": "delegation", "agent": "scout"}\n')
            f.write('{"event": "delegation", "agent": "scout"}\n')
            f.write('{"event": "delegation", "agent": "link"}\n')
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        agent_metrics = collector.get_agent_metrics()
        
        assert agent_metrics["scout"]["total"] == 2
        assert agent_metrics["link"]["total"] == 1

    def test_completion_rate_per_agent(self):
        """Should calculate completion rate per agent"""
        with open(TEST_LOG_FILE, "w") as f:
            f.write('{"event": "completion", "agent": "scout", "result": "success"}\n')
            f.write('{"event": "completion", "agent": "scout", "result": "success"}\n')
            f.write('{"event": "failure", "agent": "scout", "error": "timeout"}\n')
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        agent_metrics = collector.get_agent_metrics()
        
        assert agent_metrics["scout"]["completed"] == 2
        assert agent_metrics["scout"]["failed"] == 1

    def test_recent_delegations(self):
        """Should filter recent delegations"""
        now = datetime.utcnow()
        
        with open(TEST_LOG_FILE, "w") as f:
            # Old (more than 1 hour ago)
            old_time = (now - timedelta(hours=2)).isoformat() + "Z"
            f.write(f'{{"event": "delegation", "timestamp": "{old_time}"}}\n')
            
            # Recent (within 1 hour)
            recent_time = (now - timedelta(minutes=30)).isoformat() + "Z"
            f.write(f'{{"event": "delegation", "timestamp": "{recent_time}"}}\n')
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        metrics = collector.get_overall_metrics(hours=1)
        
        assert metrics["total_delegations"] == 1

    def test_empty_log_returns_zeros(self):
        """Empty log should return zero metrics"""
        with open(TEST_LOG_FILE, "w") as f:
            pass  # Empty file
        
        collector = MetricsCollector(log_file=TEST_LOG_FILE)
        metrics = collector.get_overall_metrics()
        
        assert metrics["total_delegations"] == 0
        assert metrics["success_rate"] == 0


class TestMetricsDashboard:
    """Test dashboard formatting."""

    def test_format_dashboard_text(self):
        """Should format metrics as readable text"""
        dashboard = MetricsDashboard()
        
        metrics = {
            "total_delegations": 10,
            "success_rate": 0.8,
            "by_agent": {
                "scout": {"total": 5, "completed": 4, "failed": 1}
            }
        }
        
        output = dashboard.format_text(metrics)
        
        assert "10" in output
        assert "80%" in output
        assert "scout" in output

    def test_format_agent_row(self):
        """Should format agent stats as table row"""
        dashboard = MetricsDashboard()
        
        agent_data = {"total": 10, "completed": 8, "failed": 2, "success_rate": 0.8}
        
        output = dashboard.format_agent_row("scout", agent_data)
        
        assert "scout" in output
        assert "10" in output
        assert "8" in output
        # Rate shows as 80% for 0.8
        assert "80%" in output or "0.8" in output