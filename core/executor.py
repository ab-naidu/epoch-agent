"""
Executor: carries out action plans autonomously.
Handles GitHub issues/PRs and API calls.
"""
import os, requests
from integrations.truefoundry import TrueFoundryObserver

class Executor:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")  # owner/repo
        self.observer = TrueFoundryObserver()

    def create_issue_for_problem(self, problem: dict) -> dict:
        """Always create a well-formed GitHub issue for a detected problem."""
        severity = problem.get("severity", 5)
        label = "critical" if severity >= 8 else "high" if severity >= 6 else "medium"
        body = (
            f"## EPOCH Autonomous Detection\n\n"
            f"**Category:** {problem.get('category', 'unknown')}\n"
            f"**Severity:** {severity}/10\n"
            f"**Probability:** {int(problem.get('probability', 0) * 100)}%\n\n"
            f"### Description\n{problem.get('description', '')}\n\n"
            f"### Predicted Impact\n{problem.get('predicted_impact', '')}\n\n"
            f"### Suggested Action\n{problem.get('suggested_action', '')}\n\n"
            f"---\n*Detected autonomously by EPOCH — no human prompt required.*"
        )
        return self._github_action({
            "params": {
                "action": "create_issue",
                "title": f"[EPOCH] {problem.get('title')}",
                "body": body,
                "labels": ["epoch-agent", label]
            }
        })

    def execute_plan(self, plan: dict) -> list[dict]:
        results = []
        for step in plan.get("steps", []):
            tool = step.get("tool")
            result = self._dispatch(tool, step)
            results.append({"step": step.get("step"), "tool": tool, "result": result})
            self.observer.log_action(f"step_{step.get('step')}_{tool}", str(result))
        return results

    def _dispatch(self, tool: str, step: dict) -> dict:
        handlers = {
            "github": self._github_action,
            "api": self._api_call,
        }
        handler = handlers.get(tool)
        return handler(step) if handler else {"status": "skipped", "reason": f"unknown tool: {tool}"}

    def _github_action(self, step: dict) -> dict:
        params = step.get("params", {})
        action = params.get("action", "create_issue")
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        base = f"https://api.github.com/repos/{self.github_repo}"

        if action == "create_issue":
            r = requests.post(f"{base}/issues", headers=headers, json={
                "title": params.get("title", "EPOCH detected issue"),
                "body": params.get("body", ""),
                "labels": params.get("labels", ["epoch-agent"])
            })
            return {"status": "created", "url": r.json().get("html_url")} if r.ok else {"status": "error", "detail": r.text}

        if action == "create_pr":
            r = requests.post(f"{base}/pulls", headers=headers, json={
                "title": params.get("title", "EPOCH automated fix"),
                "body": params.get("body", ""),
                "head": params.get("head_branch", "epoch-fix"),
                "base": params.get("base_branch", "main")
            })
            return {"status": "created", "url": r.json().get("html_url")} if r.ok else {"status": "error", "detail": r.text}

        return {"status": "skipped", "reason": f"unknown github action: {action}"}

    def _api_call(self, step: dict) -> dict:
        params = step.get("params", {})
        try:
            r = requests.request(
                params.get("method", "GET").upper(),
                params.get("url", ""),
                json=params.get("body"),
                headers=params.get("headers", {}),
                timeout=10
            )
            return {"status": r.status_code, "response": r.text[:500]}
        except Exception as e:
            return {"status": "error", "detail": str(e)}
