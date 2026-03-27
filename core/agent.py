"""
EPOCH Agent: the main autonomous loop.
Observe → Model → Simulate → Plan → Execute → Escalate → Learn
No human prompt required.
"""
import time
import logging
from core.observer import Observer
from core.world_model import WorldModel
from core.simulator import Simulator
from core.planner import Planner
from core.executor import Executor
from core.escalator import Escalator
from integrations.truefoundry import TrueFoundryObserver

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EPOCH] %(message)s")
log = logging.getLogger("epoch")

class EpochAgent:
    def __init__(self, interval_seconds: int = 60):
        self.observer = Observer()
        self.world_model = WorldModel()
        self.simulator = Simulator()
        self.planner = Planner()
        self.executor = Executor()
        self.escalator = Escalator()
        self.telemetry = TrueFoundryObserver()
        self.interval = interval_seconds
        self.running = False

    def run_once(self) -> dict:
        """Execute one full EPOCH cycle."""
        log.info("=== EPOCH cycle starting ===")
        report = {"cycle": {}, "problems": [], "actions": []}

        # 1. OBSERVE
        log.info("Observing systems...")
        signals = self.observer.observe_all()
        report["cycle"]["signals_collected"] = len(signals)

        # 2. MODEL
        log.info("Updating world model...")
        self.world_model.update(signals)
        world_state = self.world_model.get()

        # 3. SIMULATE — forward reasoning
        log.info("Running forward simulation...")
        problems = self.simulator.simulate(world_state)
        log.info(f"Detected {len(problems)} problems")

        # 4. PRIORITIZE
        prioritized = self.planner.prioritize(problems)

        for problem in prioritized:
            self.world_model.add_problem(problem)
            report["problems"].append({
                "id": problem.get("id"),
                "title": problem.get("title"),
                "severity": problem.get("severity"),
                "category": problem.get("category")
            })

            # 5. PLAN
            log.info(f"Planning for: {problem.get('title')}")
            plan = self.planner.plan(problem)

            # 6. EXECUTE or ESCALATE
            if plan.get("plan_type") == "escalate":
                log.info(f"Escalating: {problem.get('title')}")
                escalation = self.escalator.escalate(problem, plan)
                report["actions"].append({"type": "escalate", "problem": problem.get("id"), "result": escalation})

            elif plan.get("plan_type") in ["auto", "hybrid"]:
                log.info(f"Executing plan for: {problem.get('title')}")
                results = self.executor.execute_plan(plan)
                report["actions"].append({"type": "execute", "problem": problem.get("id"), "steps": results})

                if plan.get("requires_human"):
                    self.escalator.escalate(problem, plan)

                self.world_model.resolve_problem(problem.get("id"))

        self.telemetry.log_event("epoch_cycle_complete", report)
        log.info(f"=== EPOCH cycle complete: {len(problems)} problems, {len(report['actions'])} actions ===")
        return report

    def run(self):
        """Run EPOCH continuously."""
        self.running = True
        log.info("EPOCH is running autonomously. No human input required.")
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                log.error(f"Cycle error: {e}")
                self.telemetry.log_action("cycle_error", str(e), severity="error")
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        log.info("EPOCH stopped.")
