"""
Escalator: triggers Bland AI voice calls when human intervention is needed.
Non-blocking — agent continues even if escalation fails.
"""
import os
from integrations.bland import BlandAIClient
from integrations.truefoundry import TrueFoundryObserver

class Escalator:
    def __init__(self):
        self.bland = BlandAIClient()
        self.observer = TrueFoundryObserver()
        self.oncall_number = os.getenv("ONCALL_PHONE_NUMBER", "")

    def escalate(self, problem: dict, plan: dict) -> dict:
        if not self.oncall_number or self.oncall_number == "+1xxxxxxxxxx":
            return {"status": "skipped", "reason": "no oncall number configured"}

        task = (
            f"This is EPOCH, an autonomous monitoring agent. "
            f"I've detected a critical issue: {problem.get('title')}. "
            f"{problem.get('description')}. "
            f"Predicted impact: {problem.get('predicted_impact')}. "
            f"Escalation reason: {plan.get('escalation_reason', 'requires human decision')}. "
            f"Please acknowledge and take action immediately."
        )

        try:
            result = self.bland.call(
                to_number=self.oncall_number,
                task=task,
                context=f"Problem severity: {problem.get('severity')}/10"
            )
            self.observer.log_action("escalate_call", str(result), severity="critical")
            return result
        except Exception as e:
            self.observer.log_action("escalate_failed", str(e), severity="error")
            return {"status": "error", "detail": str(e)}
