"""
EPOCH Test Suite — validates all core components and integrations.
Run: python -m pytest tests/ -v
"""
import pytest, json, os, sys
from unittest.mock import MagicMock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Memory / Aerospike fallback ───────────────────────────────────────────────

class TestAerospikeMemory:
    def setup_method(self):
        from integrations.aerospike import AerospikeMemory
        self.mem = AerospikeMemory()

    def test_write_and_read(self):
        self.mem.write("test_set", "key1", {"value": 42})
        result = self.mem.read("test_set", "key1")
        assert result["value"] == 42

    def test_read_missing_key_returns_none(self):
        result = self.mem.read("test_set", "nonexistent_key_xyz")
        assert result is None

    def test_write_adds_timestamp(self):
        self.mem.write("test_set", "key2", {"data": "hello"})
        result = self.mem.read("test_set", "key2")
        assert "_updated_at" in result

    def test_delete(self):
        self.mem.write("test_set", "key3", {"temp": True})
        self.mem.delete("test_set", "key3")
        assert self.mem.read("test_set", "key3") is None

    def test_scan_all(self):
        self.mem.write("scan_set", "a", {"x": 1})
        self.mem.write("scan_set", "b", {"x": 2})
        results = self.mem.scan_all("scan_set")
        assert len(results) >= 2


# ── World Model ───────────────────────────────────────────────────────────────

class TestWorldModel:
    def setup_method(self):
        from core.world_model import WorldModel
        self.wm = WorldModel()

    def test_update_and_get(self):
        self.wm.update({"cpu": "high", "errors": 42})
        state = self.wm.get()
        assert state["cpu"] == "high"
        assert state["errors"] == 42

    def test_add_and_get_problems(self):
        problem = {"id": "test-p1", "title": "Test Problem", "severity": 7}
        self.wm.add_problem(problem)
        problems = self.wm.get_problems()
        ids = [p["id"] for p in problems]
        assert "test-p1" in ids

    def test_resolve_problem(self):
        self.wm.add_problem({"id": "test-p2", "title": "Resolve Me", "severity": 5})
        self.wm.resolve_problem("test-p2")
        problems = self.wm.get_problems()
        resolved = [p for p in problems if p["id"] == "test-p2"]
        assert resolved[0]["status"] == "resolved"

    def test_problem_has_detected_at(self):
        self.wm.add_problem({"id": "test-p3", "title": "Timestamp Test", "severity": 3})
        problems = self.wm.get_problems()
        p = next(p for p in problems if p["id"] == "test-p3")
        assert "detected_at" in p


# ── Bedrock Reasoner ──────────────────────────────────────────────────────────

class TestBedrockReasoner:
    def test_reason_returns_string(self):
        from integrations.bedrock import BedrockReasoner
        reasoner = BedrockReasoner()
        with patch.object(reasoner, 'client') as mock_client:
            mock_body = MagicMock()
            mock_body.read.return_value = json.dumps({
                "output": {
                    "message": {
                        "content": [{"text": "mocked response"}]
                    }
                }
            }).encode()
            mock_client.invoke_model.return_value = {"body": mock_body}
            result = reasoner.reason("system prompt", "user prompt")
            assert isinstance(result, str)
            assert len(result) > 0

    def test_reason_called_with_correct_model(self):
        from integrations.bedrock import BedrockReasoner
        reasoner = BedrockReasoner()
        assert "nova" in reasoner.model_id or "claude" in reasoner.model_id or "amazon" in reasoner.model_id


# ── Simulator ─────────────────────────────────────────────────────────────────

class TestSimulator:
    def test_simulate_returns_list(self):
        from core.simulator import Simulator
        sim = Simulator()
        mock_response = json.dumps([
            {
                "id": "p1",
                "title": "Test Issue",
                "description": "Something is wrong",
                "severity": 8,
                "probability": 0.9,
                "fixability": 7,
                "predicted_impact": "Outage",
                "suggested_action": "Fix it",
                "category": "reliability"
            }
        ])
        with patch.object(sim.reasoner, 'reason', return_value=mock_response):
            problems = sim.simulate({"cpu": "high"})
            assert isinstance(problems, list)
            assert len(problems) == 1
            assert problems[0]["title"] == "Test Issue"

    def test_simulate_handles_bad_json(self):
        from core.simulator import Simulator
        sim = Simulator()
        with patch.object(sim.reasoner, 'reason', return_value="not valid json at all"):
            problems = sim.simulate({})
            assert problems == []

    def test_simulate_assigns_id_if_missing(self):
        from core.simulator import Simulator
        sim = Simulator()
        mock_response = json.dumps([{
            "title": "No ID Problem",
            "severity": 5,
            "probability": 0.5,
            "fixability": 5,
            "category": "performance"
        }])
        with patch.object(sim.reasoner, 'reason', return_value=mock_response):
            problems = sim.simulate({})
            assert problems[0].get("id") is not None


# ── Planner ───────────────────────────────────────────────────────────────────

class TestPlanner:
    def test_plan_returns_dict(self):
        from core.planner import Planner
        planner = Planner()
        mock_plan = json.dumps({
            "problem_id": "p1",
            "plan_type": "auto",
            "steps": [{"step": 1, "action": "fix", "tool": "github", "params": {}}],
            "requires_human": False,
            "escalation_reason": ""
        })
        with patch.object(planner.reasoner, 'reason', return_value=mock_plan):
            plan = planner.plan({"id": "p1", "title": "Test"})
            assert plan["plan_type"] == "auto"
            assert isinstance(plan["steps"], list)

    def test_plan_falls_back_on_bad_json(self):
        from core.planner import Planner
        planner = Planner()
        with patch.object(planner.reasoner, 'reason', return_value="garbage"):
            plan = planner.plan({"id": "p1", "title": "Test"})
            assert plan["plan_type"] == "escalate"
            assert plan["requires_human"] is True

    def test_prioritize_sorts_by_score(self):
        from core.planner import Planner
        planner = Planner()
        problems = [
            {"id": "low", "severity": 2, "probability": 0.3, "fixability": 5},
            {"id": "high", "severity": 9, "probability": 0.9, "fixability": 5},
            {"id": "mid", "severity": 5, "probability": 0.5, "fixability": 5},
        ]
        sorted_problems = planner.prioritize(problems)
        assert sorted_problems[0]["id"] == "high"
        assert sorted_problems[-1]["id"] == "low"


# ── Executor ──────────────────────────────────────────────────────────────────

class TestExecutor:
    def test_execute_plan_runs_steps(self):
        from core.executor import Executor
        executor = Executor()
        plan = {
            "steps": [
                {"step": 1, "tool": "github", "params": {"action": "create_issue", "title": "Test", "body": "body"}},
            ]
        }
        with patch.object(executor, '_github_action', return_value={"status": "created", "url": "http://test"}):
            results = executor.execute_plan(plan)
            assert results[0]["result"]["status"] == "created"

    def test_unknown_tool_skipped(self):
        from core.executor import Executor
        executor = Executor()
        plan = {"steps": [{"step": 1, "tool": "unknown_tool_xyz", "params": {}}]}
        results = executor.execute_plan(plan)
        assert results[0]["result"]["status"] == "skipped"

    def test_create_issue_for_problem(self):
        from core.executor import Executor
        executor = Executor()
        problem = {
            "id": "p1", "title": "DB Slow", "severity": 8,
            "category": "performance", "probability": 0.9,
            "description": "Queries are slow",
            "predicted_impact": "Outage",
            "suggested_action": "Add index"
        }
        with patch.object(executor, '_github_action', return_value={"status": "created", "url": "http://test"}) as mock:
            executor.create_issue_for_problem(problem)
            call_args = mock.call_args[0][0]
            assert "[EPOCH]" in call_args["params"]["title"]
            assert "severity" in call_args["params"]["body"].lower() or "Severity" in call_args["params"]["body"]


# ── Observer ──────────────────────────────────────────────────────────────────

class TestObserver:
    def test_observe_system_metrics_returns_dict(self):
        from core.observer import Observer
        obs = Observer()
        metrics = obs.observe_system_metrics()
        assert isinstance(metrics, dict)
        assert "error_rate_trend" in metrics

    def test_observe_all_has_expected_keys(self):
        from core.observer import Observer
        obs = Observer()
        with patch.object(obs, 'observe_github', return_value={"commits": [], "pulls": []}):
            result = obs.observe_all()
            assert "github" in result
            assert "system_metrics" in result


# ── Escalator ─────────────────────────────────────────────────────────────────

class TestEscalator:
    def test_skips_when_no_number_configured(self):
        from core.escalator import Escalator
        esc = Escalator()
        esc.oncall_number = ""
        result = esc.escalate({"title": "Test"}, {})
        assert result["status"] == "skipped"

    def test_skips_placeholder_number(self):
        from core.escalator import Escalator
        esc = Escalator()
        esc.oncall_number = "+1xxxxxxxxxx"
        result = esc.escalate({"title": "Test"}, {})
        assert result["status"] == "skipped"

    def test_handles_bland_api_error_gracefully(self):
        from core.escalator import Escalator
        esc = Escalator()
        esc.oncall_number = "+15551234567"
        with patch.object(esc.bland, 'call', side_effect=Exception("API error")):
            result = esc.escalate({"title": "Test", "severity": 8}, {"escalation_reason": "test"})
            assert result["status"] == "error"


# ── Full Agent Cycle (integration) ────────────────────────────────────────────

class TestAgentCycle:
    def test_run_once_returns_report(self):
        from core.agent import EpochAgent
        agent = EpochAgent()

        mock_problems = [
            {"id": "p1", "title": "Test Problem", "severity": 8,
             "probability": 0.9, "fixability": 7, "category": "reliability",
             "description": "desc", "predicted_impact": "impact", "suggested_action": "fix"}
        ]
        mock_plan = {
            "problem_id": "p1", "plan_type": "auto",
            "steps": [], "requires_human": False, "escalation_reason": ""
        }

        with patch.object(agent.observer, 'observe_all', return_value={"github": {}, "metrics": {}}), \
             patch.object(agent.simulator, 'simulate', return_value=mock_problems), \
             patch.object(agent.planner, 'plan', return_value=mock_plan), \
             patch.object(agent.executor, 'create_issue_for_problem', return_value={"status": "created"}), \
             patch.object(agent.executor, 'execute_plan', return_value=[]):
            report = agent.run_once()
            assert "problems" in report
            assert "actions" in report
            assert len(report["problems"]) == 1
            assert report["problems"][0]["title"] == "Test Problem"
