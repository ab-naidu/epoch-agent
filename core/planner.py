"""
Planner: generates autonomous action plans for each detected problem.
No human prompt needed — goals are derived from the world model.
"""
import json
from integrations.bedrock import BedrockReasoner
from integrations.truefoundry import TrueFoundryObserver

SYSTEM_PROMPT = """You are EPOCH's autonomous planning engine.
Given a detected problem, generate a concrete step-by-step action plan.
Each step must be executable by a software agent — no vague instructions.

Return ONLY valid JSON with this structure:
{
  "problem_id": "...",
  "plan_type": "auto" | "escalate" | "hybrid",
  "steps": [
    {
      "step": 1,
      "action": "action_type",
      "description": "what to do",
      "tool": "github | bash | api | bland_call",
      "params": {}
    }
  ],
  "requires_human": true | false,
  "escalation_reason": "..." 
}

plan_type:
- auto: agent can fully resolve without human
- escalate: requires human intervention via voice call
- hybrid: agent does partial fix, human handles the rest
"""

class Planner:
    def __init__(self):
        self.reasoner = BedrockReasoner()
        self.observer = TrueFoundryObserver()

    def plan(self, problem: dict) -> dict:
        prompt = f"Problem to solve:\n{json.dumps(problem, indent=2)}"
        raw = self.reasoner.reason(SYSTEM_PROMPT, prompt)
        self.observer.log_reasoning_trace("plan", problem.get("title", ""), raw[:500])

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {
                "problem_id": problem.get("id"),
                "plan_type": "escalate",
                "steps": [],
                "requires_human": True,
                "escalation_reason": "Failed to generate automated plan"
            }

    def prioritize(self, problems: list[dict]) -> list[dict]:
        """Sort problems by composite score: severity × probability / fixability."""
        def score(p):
            return (p.get("severity", 5) * p.get("probability", 0.5)) / max(p.get("fixability", 5), 1)
        return sorted(problems, key=score, reverse=True)
