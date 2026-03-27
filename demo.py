"""
EPOCH Demo Script — for the 3-minute hackathon presentation.
Simulates a full cycle with mock data so it runs without live API keys.
"""
import json, time

MOCK_WORLD_STATE = {
    "github": {
        "commits": [{"sha": "abc123", "commit": {"message": "fix: patch auth middleware"}}],
        "pulls": [],
        "issues": [{"title": "Memory leak in worker process", "state": "open"}],
        "actions/runs": [{"conclusion": "failure", "name": "CI Pipeline"}]
    },
    "system_metrics": {
        "cpu_trend": "rising",
        "error_rate_trend": "rising",
        "latency_p99_ms": 890,
        "db_query_slow_count": 12
    }
}

MOCK_PROBLEMS = [
    {
        "id": "p001",
        "title": "Database query degradation — outage risk in ~48h",
        "description": "Slow query count has grown 4x in 6 hours. At current growth rate, DB will hit connection limit within 48 hours.",
        "severity": 9,
        "probability": 0.87,
        "fixability": 8,
        "predicted_impact": "Full service outage affecting all users",
        "suggested_action": "Add index on users.created_at, optimize top 3 slow queries",
        "category": "performance"
    },
    {
        "id": "p002",
        "title": "CI pipeline failing — deployment blocked",
        "description": "Last 3 CI runs failed. No deployments possible until resolved.",
        "severity": 7,
        "probability": 1.0,
        "fixability": 9,
        "predicted_impact": "No new code can ship until fixed",
        "suggested_action": "Open GitHub issue, notify team",
        "category": "reliability"
    }
]

def demo():
    print("\n" + "="*60)
    print("  EPOCH — Autonomous Predictive Agent")
    print("  Deep Agents Hackathon | AWS Builder Loft")
    print("="*60)

    print("\n[1/5] OBSERVING systems...")
    time.sleep(1)
    print(f"  ✓ GitHub signals collected")
    print(f"  ✓ System metrics collected")
    print(f"  ✓ World model updated in Aerospike")

    print("\n[2/5] SIMULATING forward — what breaks in 72 hours?")
    time.sleep(1.5)
    print(f"  ✓ AWS Bedrock reasoning complete")
    print(f"  ✓ {len(MOCK_PROBLEMS)} problems detected")

    print("\n[3/5] PROBLEMS detected (prioritized by severity × probability):")
    for p in MOCK_PROBLEMS:
        score = round(p['severity'] * p['probability'], 1)
        print(f"  [{score:4.1f}] {p['title']}")
        print(f"         → {p['suggested_action']}")

    print("\n[4/5] EXECUTING autonomous actions...")
    time.sleep(1)
    print("  ✓ GitHub issue created: 'DB query degradation — EPOCH alert'")
    print("  ✓ GitHub issue created: 'CI pipeline failure — EPOCH alert'")
    print("  ✓ Actions logged to TrueFoundry observability")

    print("\n[5/5] ESCALATING via Bland AI voice call...")
    time.sleep(1)
    print("  ✓ On-call engineer called: 'Critical DB issue detected, action required'")

    print("\n" + "="*60)
    print("  EPOCH cycle complete. Zero human prompts used.")
    print("  Problems found: 2 | Actions taken: 3 | Humans called: 1")
    print("="*60 + "\n")

if __name__ == "__main__":
    demo()
