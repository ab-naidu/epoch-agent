"""
Observer: ingests live signals from connected systems via Airbyte.
Produces a raw signal feed for the world model.
"""
import os, requests
from integrations.airbyte import AirbyteClient

class Observer:
    def __init__(self):
        self.airbyte = AirbyteClient()
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")  # owner/repo

    def observe_github(self) -> dict:
        """Pull recent commits, open PRs, issues, and workflow runs."""
        headers = {"Authorization": f"token {self.github_token}"}
        base = f"https://api.github.com/repos/{self.github_repo}"
        signals = {}

        for endpoint in ["commits", "pulls", "issues", "actions/runs"]:
            try:
                r = requests.get(f"{base}/{endpoint}?per_page=10", headers=headers)
                signals[endpoint] = r.json() if r.ok else []
            except Exception:
                signals[endpoint] = []

        return signals

    def observe_system_metrics(self) -> dict:
        """Placeholder — connect to CloudWatch, Datadog, etc."""
        return {
            "cpu_trend": "stable",
            "error_rate_trend": "rising",
            "latency_p99_ms": 420,
            "db_query_slow_count": 3
        }

    def observe_all(self) -> dict:
        """Aggregate all signals into one observation payload."""
        return {
            "github": self.observe_github(),
            "system_metrics": self.observe_system_metrics(),
        }
