"""
Metrics Dashboard
Calculate and display delegation metrics
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict


class MetricsCollector:
    """Collect metrics from delegation logs."""
    
    def __init__(self, log_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/delegation.log"):
        self.log_file = log_file
    
    def _read_logs(self, hours: int = None) -> List[Dict]:
        """Read and parse log entries"""
        if not os.path.exists(self.log_file):
            return []
        
        logs = []
        cutoff = None
        if hours:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    # Filter by time if specified
                    if cutoff and "timestamp" in entry:
                        log_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                        if log_time.replace(tzinfo=None) < cutoff:
                            continue
                    
                    logs.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    def get_overall_metrics(self, hours: int = None) -> Dict[str, Any]:
        """Get overall system metrics"""
        logs = self._read_logs(hours)
        
        delegations = [l for l in logs if l.get("event") == "delegation"]
        completions = [l for l in logs if l.get("event") == "completion"]
        failures = [l for l in logs if l.get("event") == "failure"]
        
        successful = len([c for c in completions if c.get("result") == "success"])
        
        total = len(delegations)
        success_rate = successful / total if total > 0 else 0
        
        return {
            "total_delegations": total,
            "completed": len(completions),
            "failed": len(failures),
            "success_rate": round(success_rate, 2),
            "period_hours": hours if hours else "all"
        }
    
    def get_agent_metrics(self, hours: int = None) -> Dict[str, Dict]:
        """Get per-agent metrics"""
        logs = self._read_logs(hours)
        
        agent_data = defaultdict(lambda: {"total": 0, "completed": 0, "failed": 0})
        
        for log in logs:
            agent = log.get("agent")
            if not agent:
                continue
            
            if log.get("event") == "delegation":
                agent_data[agent]["total"] += 1
            
            if log.get("event") == "completion":
                agent_data[agent]["completed"] += 1
            
            if log.get("event") == "failure":
                agent_data[agent]["failed"] += 1
        
        # Calculate success rates
        for agent, data in agent_data.items():
            total = data["total"]
            if total > 0:
                data["success_rate"] = round(data["completed"] / total, 2)
            else:
                data["success_rate"] = 0
        
        return dict(agent_data)
    
    def get_latency_stats(self, hours: int = None) -> Dict[str, Any]:
        """Get latency statistics"""
        logs = self._read_logs(hours)
        
        latencies = []
        for log in logs:
            if log.get("duration_ms"):
                latencies.append(log["duration_ms"])
        
        if not latencies:
            return {"avg_ms": 0, "min_ms": 0, "max_ms": 0, "count": 0}
        
        return {
            "avg_ms": round(sum(latencies) / len(latencies), 1),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "count": len(latencies)
        }
    
    def get_time_series(self, hours: int = 24) -> List[Dict]:
        """Get hourly breakdown of delegations"""
        logs = self._read_logs(hours=hours)
        
        hourly = defaultdict(lambda: {"delegations": 0, "completed": 0, "failed": 0})
        
        for log in logs:
            if "timestamp" not in log:
                continue
            
            try:
                log_time = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
                hour_key = log_time.strftime("%Y-%m-%d %H:00")
                
                if log.get("event") == "delegation":
                    hourly[hour_key]["delegations"] += 1
                if log.get("event") == "completion":
                    hourly[hour_key]["completed"] += 1
                if log.get("event") == "failure":
                    hourly[hour_key]["failed"] += 1
            except:
                continue
        
        # Sort by hour
        sorted_data = sorted(hourly.items(), key=lambda x: x[0])
        
        return [
            {"hour": k, "delegations": v["delegations"], "completed": v["completed"], "failed": v["failed"]}
            for k, v in sorted_data
        ]


class MetricsDashboard:
    """Format metrics for display."""
    
    def format_text(self, metrics: Dict) -> str:
        """Format metrics as readable text"""
        lines = []
        lines.append("=" * 50)
        lines.append("  DELEGATION SYSTEM METRICS")
        lines.append("=" * 50)
        
        lines.append(f"\n📊 Overall:")
        lines.append(f"  Total delegations: {metrics.get('total_delegations', 0)}")
        lines.append(f"  Completed: {metrics.get('completed', 0)}")
        lines.append(f"  Failed: {metrics.get('failed', 0)}")
        lines.append(f"  Success rate: {int(metrics.get('success_rate', 0) * 100)}%")
        
        if "by_agent" in metrics:
            lines.append(f"\n🤖 By Agent:")
            lines.append("-" * 40)
            lines.append(f"  {'Agent':<10} {'Total':<8} {'OK':<6} {'Fail':<6} {'Rate':<8}")
            lines.append("-" * 40)
            
            for agent, data in metrics["by_agent"].items():
                rate = int(data.get("success_rate", 0) * 100)
                lines.append(f"  {agent:<10} {data['total']:<8} {data['completed']:<6} {data['failed']:<6} {rate}%")
        
        lines.append("\n" + "=" * 50)
        
        return "\n".join(lines)
    
    def format_agent_row(self, agent: str, data: Dict) -> str:
        """Format single agent as table row"""
        rate = int(data.get("success_rate", 0) * 100)
        return f"{agent:<10} | {data['total']:>4} | {data['completed']:>4} | {data['failed']:>4} | {rate:>3}%"


def print_dashboard():
    """Print full dashboard"""
    collector = MetricsCollector()
    dashboard = MetricsDashboard()
    
    # Get all metrics
    overall = collector.get_overall_metrics()
    by_agent = collector.get_agent_metrics()
    
    # Combine
    metrics = {
        **overall,
        "by_agent": by_agent
    }
    
    print(dashboard.format_text(metrics))


if __name__ == "__main__":
    import sys
    
    collector = MetricsCollector()
    dashboard = MetricsDashboard()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "agents":
            metrics = collector.get_agent_metrics()
            for agent, data in metrics.items():
                print(dashboard.format_agent_row(agent, data))
        elif sys.argv[1] == "hours":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            metrics = collector.get_overall_metrics(hours=hours)
            print(json.dumps(metrics, indent=2))
        elif sys.argv[1] == "series":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            data = collector.get_time_series(hours=hours)
            print(json.dumps(data, indent=2))
    else:
        print_dashboard()