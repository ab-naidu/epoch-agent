"""
Aerospike memory layer — uses local JSON file as fallback when Aerospike
server is not available (e.g. local dev / hackathon demo).
In production, swap the JSONMemory backend for the real aerospike client.
"""
import os, json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / ".epoch_data"

class AerospikeMemory:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    def _path(self, set_name: str, key: str) -> Path:
        return DATA_DIR / f"{set_name}__{key}.json"

    def write(self, set_name: str, key: str, data: dict):
        data["_updated_at"] = datetime.utcnow().isoformat()
        with open(self._path(set_name, key), "w") as f:
            json.dump(data, f, indent=2, default=str)

    def read(self, set_name: str, key: str) -> dict | None:
        p = self._path(set_name, key)
        if not p.exists():
            return None
        with open(p) as f:
            return json.load(f)

    def delete(self, set_name: str, key: str):
        p = self._path(set_name, key)
        if p.exists():
            p.unlink()

    def scan_all(self, set_name: str) -> list[dict]:
        results = []
        for f in DATA_DIR.glob(f"{set_name}__*.json"):
            with open(f) as fp:
                results.append(json.load(fp))
        return results
