"""
Analytics and Reporting
Generate delegation reports and analytics
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class Analytics:
    """Collect and analyze delegation data."""
    
    def __init__(self, analytics_file: str = "/Users/soup/.openclaw/workspace/delegation/memory/analytics.json"):
        self.analytics_file = analytics_file
        self._ensure_file()
        self.data = self._load()
    
    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.analytics_file), exist_ok=True)
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, "w") as f:
                json.dump({"delegations": []}, f)
    
    def _load(self) -> Dict:
        with open(self.analytics_file, "r") as f:
            return json.load(f)
    
    def _save(self):
        with open(self.analytics_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def record_delegation(
        self,
        agent: str,
        status: str,
        latency_ms: int,
        timestamp: str = None
    ):
        """Record a delegation for analytics."""
        entry = {
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "agent": agent,
            "status": status,  # "success" or "failed"
            "latency_ms": latency_ms
        }
        
        if "delegations" not in self.data:
            self.data["delegations"] = []
        
        self.data["delegations"].append(entry)
        
        # Keep last 10,000 entries
        if len(self.data["delegations"]) > 10000:
            self.data["delegations"] = self.data["delegations"][-10000:]
        
        self._save()
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report."""
        delegations = self.data.get("delegations", [])
        
        if not delegations:
            return {"total_delegations": 0, "agents": {}}
        
        # Overall stats
        total = len(delegations)
        successes = sum(1 for d in delegations if d["status"] == "success")
        
        # Per-agent stats
        agent_data = defaultdict(lambda: {"success": 0, "failed": 0, "latencies": []})
        
        for d in delegations:
            agent = d["agent"]
            if d["status"] == "success":
                agent_data[agent]["success"] += 1
            else:
                agent_data[agent]["failed"] += 1
            agent_data[agent]["latencies"].append(d.get("latency_ms", 0))
        
        # Build report
        report = {
            "total_delegations": total,
            "success_count": successes,
            "failed_count": total - successes,
            "success_rate": round(successes / total, 2) if total > 0 else 0,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Add per-agent breakdown
        for agent, stats in agent_data.items():
            avg_latency = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
            report[agent] = {
                "success_count": stats["success"],
                "failed_count": stats["failed"],
                "avg_latency_ms": round(avg_latency, 1)
            }
        
        return report
    
    def get_hourly_stats(self, hours: int = 24) -> List[Dict]:
        """Get hourly breakdown of delegations."""
        delegations = self.data.get("delegations", [])
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Group by hour
        hourly = defaultdict(lambda: {"delegations": 0, "success": 0, "failed": 0})
        
        for d in delegations:
            timestamp = datetime.fromisoformat(d["timestamp"])
            if timestamp >= cutoff:
                hour_key = timestamp.strftime("%Y-%m-%d %H:00")
                hourly[hour_key]["delegations"] += 1
                if d["status"] == "success":
                    hourly[hour_key]["success"] += 1
                else:
                    hourly[hour_key]["failed"] += 1
        
        # Sort and return
        sorted_hours = sorted(hourly.items(), key=lambda x: x[0])
        
        return [
            {"hour": k, "delegations": v["delegations"], "success": v["success"], "failed": v["failed"]}
            for k, v in sorted_hours
        ]
    
    def get_agent_rankings(self) -> List[Dict]:
        """Rank agents by performance."""
        delegations = self.data.get("delegations", [])
        
        agent_stats = defaultdict(lambda: {"success": 0, "total": 0, "latency_sum": 0})
        
        for d in delegations:
            agent = d["agent"]
            agent_stats[agent]["total"] += 1
            if d["status"] == "success":
                agent_stats[agent]["success"] += 1
            agent_stats[agent]["latency_sum"] += d.get("latency_ms", 0)
        
        # Calculate scores
        rankings = []
        for agent, stats in agent_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            avg_latency = stats["latency_sum"] / stats["total"] if stats["total"] > 0 else 0
            
            # Score: 70% success rate, 30% speed
            score = (success_rate * 0.7) + (max(0, (500 - avg_latency)) / 500 * 0.3)
            
            rankings.append({
                "agent": agent,
                "success_rate": round(success_rate, 2),
                "avg_latency_ms": round(avg_latency, 1),
                "total_tasks": stats["total"],
                "score": round(score, 2)
            })
        
        # Sort by score
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, r in enumerate(rankings):
            r["rank"] = i + 1
        
        return rankings
    
    def export_json(self) -> str:
        """Export analytics as JSON string."""
        return json.dumps(self.generate_report(), indent=2)


class DelegationReport:
    """Generate formatted delegation reports."""
    
    @staticmethod
    def format_text(report: Dict) -> str:
        """Format report as readable text."""
        lines = []
        
        lines.append("=" * 60)
        lines.append("DELEGATION ANALYTICS REPORT")
        lines.append("=" * 60)
        
        lines.append(f"\nTotal Delegations: {report.get('total_delegations', 0)}")
        lines.append(f"Success Rate: {int(report.get('success_rate', 0) * 100)}%")
        
        lines.append("\n--- Per Agent ---")
        
        for key, value in report.items():
            if key not in ["total_delegations", "success_count", "failed_count", "success_rate", "generated_at"]:
                lines.append(f"{key}: {value.get('success_count', 0)} OK, {value.get('failed_count', 0)} failed, {value.get('avg_latency_ms', 0)}ms avg")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    analytics = Analytics()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            print(DelegationReport.format_text(analytics.generate_report()))
        elif sys.argv[1] == "rankings":
            import json
            print(json.dumps(analytics.get_agent_rankings(), indent=2))
        elif sys.argv[1] == "hourly":
            import json
            print(json.dumps(analytics.get_hourly_stats(), indent=2))
    else:
        print("Usage: analytics.py <report|rankings|hourly>")