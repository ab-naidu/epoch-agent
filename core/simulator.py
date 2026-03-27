"""
Simulator: runs forward reasoning over the world model.
Predicts what breaks next and scores problems by severity × probability × fixability.
"""
import json, uuid
from integrations.bedrock import BedrockReasoner
from integrations.truefoundry import TrueFoundryObserver

SYSTEM_PROMPT = """You are EPOCH's forward simulation engine.
Given a snapshot of a system's current state and signals, your job is to:
1. Identify latent problems that exist RIGHT NOW but haven't surfaced yet
2. Predict what will break in the next 24-72 hours based on trends
3. Score each problem: severity (1-10), probability (0-1), fixability (1-10)
4. Return ONLY valid JSON — a list of problem objects.

Each problem object must have:
- id: unique string
- title: short description
- description: detailed explanation
- severity: 1-10
- probability: 0.0-1.0
- fixability: 1-10 (10 = fully automatable fix)
- predicted_impact: what happens if not fixed
- suggested_action: what should be done
- category: one of [security, performance, reliability, cost, code_quality]
"""

class Simulator:
    def __init__(self):
        self.reasoner = BedrockReasoner()
        self.observer = TrueFoundryObserver()

    def simulate(self, world_state: dict) -> list[dict]:
        """Run forward simulation and return prioritized problem list."""
        prompt = f"Current system state:\n{json.dumps(world_state, indent=2, default=str)}"

        raw = self.reasoner.reason(SYSTEM_PROMPT, prompt)
        self.observer.log_reasoning_trace("simulate", prompt[:500], raw[:500])

        try:
            # Extract JSON from response
            start = raw.find("[")
            end = raw.rfind("]") + 1
            problems = json.loads(raw[start:end])
            # Ensure each problem has a unique id
            for p in problems:
                if not p.get("id"):
                    p["id"] = str(uuid.uuid4())[:8]
            return problems
        except Exception:
            return []
