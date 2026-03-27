import os, requests

class AirbyteClient:
    def __init__(self):
        self.base_url = os.getenv("AIRBYTE_API_URL", "http://localhost:8000")
        self.headers = {
            "Authorization": f"Bearer {os.getenv('AIRBYTE_API_KEY', '')}",
            "Content-Type": "application/json"
        }

    def list_connections(self) -> list:
        resp = requests.get(f"{self.base_url}/v1/connections", headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def trigger_sync(self, connection_id: str) -> dict:
        resp = requests.post(
            f"{self.base_url}/v1/jobs",
            headers=self.headers,
            json={"connectionId": connection_id, "jobType": "sync"}
        )
        resp.raise_for_status()
        return resp.json()

    def get_sync_status(self, job_id: str) -> dict:
        resp = requests.get(f"{self.base_url}/v1/jobs/{job_id}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def ingest_source(self, source_name: str, config: dict) -> dict:
        """Create a new source and trigger sync."""
        resp = requests.post(
            f"{self.base_url}/v1/sources",
            headers=self.headers,
            json={"name": source_name, "configuration": config}
        )
        resp.raise_for_status()
        return resp.json()
