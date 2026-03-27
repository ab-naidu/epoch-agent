"""
World Model: maintains a real-time understanding of system state in Aerospike.
Updated continuously by the observer, read by the simulator and planner.
"""
import json
from datetime import datetime
from integrations.aerospike import AerospikeMemory

class WorldModel:
    SET = "world_model"

    def __init__(self):
        self.memory = AerospikeMemory()

    def update(self, signals: dict):
        """Merge new signals into the world model."""
        current = self.memory.read(self.SET, "current") or {}
        current.update(signals)
        current["last_updated"] = datetime.utcnow().isoformat()
        self.memory.write(self.SET, "current", current)

    def get(self) -> dict:
        return self.memory.read(self.SET, "current") or {}

    def add_problem(self, problem: dict):
        """Record a detected problem with severity and prediction."""
        problems = self.memory.read(self.SET, "problems") or {"items": []}
        problem["detected_at"] = datetime.utcnow().isoformat()
        problems["items"].append(problem)
        self.memory.write(self.SET, "problems", problems)

    def get_problems(self) -> list:
        data = self.memory.read(self.SET, "problems") or {"items": []}
        return data["items"]

    def resolve_problem(self, problem_id: str):
        problems = self.memory.read(self.SET, "problems") or {"items": []}
        for p in problems["items"]:
            if p.get("id") == problem_id:
                p["status"] = "resolved"
                p["resolved_at"] = datetime.utcnow().isoformat()
        self.memory.write(self.SET, "problems", problems)
