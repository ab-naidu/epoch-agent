import os, requests

class BlandAIClient:
    def __init__(self):
        self.api_key = os.getenv("BLAND_API_KEY")
        self.from_number = os.getenv("BLAND_PHONE_NUMBER")
        self.base_url = "https://api.bland.ai/v1"
        self.headers = {"authorization": self.api_key}

    def call(self, to_number: str, task: str, context: str = "") -> dict:
        """Trigger an autonomous voice call to escalate an issue."""
        payload = {
            "phone_number": to_number,
            "from": self.from_number,
            "task": task,
            "voice": "nat",
            "wait_for_greeting": True,
            "record": True,
            "answered_by_enabled": True,
            "noise_cancellation": True,
            "request_data": {"context": context},
            "model": "enhanced"
        }
        resp = requests.post(f"{self.base_url}/calls", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_call_status(self, call_id: str) -> dict:
        resp = requests.get(f"{self.base_url}/calls/{call_id}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()
