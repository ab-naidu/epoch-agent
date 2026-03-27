import os, requests, json
from datetime import datetime

class TrueFoundryObserver:
    def __init__(self):
        self.api_key = os.getenv("TRUEFOUNDRY_API_KEY")
        self.base_url = "https://app.truefoundry.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def log_event(self, event_type: str, data: dict):
        """Log an agent event for observability."""
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        try:
            requests.post(
                f"{self.base_url}/v1/logs",
                headers=self.headers,
                json=payload,
                timeout=3
            )
        except Exception:
            # Non-blocking — observability should never break the agent
            pass

    def log_reasoning_trace(self, step: str, input: str, output: str, metadata: dict = {}):
        self.log_event("reasoning_trace", {
            "step": step,
            "input": input,
            "output": output,
            **metadata
        })

    def log_action(self, action: str, result: str, severity: str = "info"):
        self.log_event("agent_action", {
            "action": action,
            "result": result,
            "severity": severity
        })
