"""
EPOCH FastAPI — exposes agent status, manual triggers, and Auth0-protected endpoints.
"""
import threading
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from core.agent import EpochAgent
from core.world_model import WorldModel
from integrations.auth0 import Auth0Client

app = FastAPI(title="EPOCH Agent API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

agent = EpochAgent(interval_seconds=60)
world_model = WorldModel()
auth0 = Auth0Client()
agent_thread = None

# ── Auth dependency ──────────────────────────────────────────────────────────

def verify_auth(authorization: str = Header(...)) -> dict:
    token = authorization.replace("Bearer ", "")
    try:
        return auth0.verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "agent_running": agent.running}

@app.post("/agent/start")
def start_agent():
    global agent_thread
    if agent.running:
        return {"status": "already running"}
    agent_thread = threading.Thread(target=agent.run, daemon=True)
    agent_thread.start()
    return {"status": "started"}

@app.post("/agent/stop")
def stop_agent():
    agent.stop()
    return {"status": "stopped"}

@app.post("/agent/run-once")
def run_once(user: dict = Depends(verify_auth)):
    """Trigger a single EPOCH cycle — Auth0 protected."""
    report = agent.run_once()
    return report

@app.get("/world-model")
def get_world_model(user: dict = Depends(verify_auth)):
    return world_model.get()

@app.get("/problems")
def get_problems(user: dict = Depends(verify_auth)):
    return {"problems": world_model.get_problems()}

@app.get("/problems/open")
def get_open_problems(user: dict = Depends(verify_auth)):
    all_problems = world_model.get_problems()
    open_problems = [p for p in all_problems if p.get("status") != "resolved"]
    return {"problems": open_problems, "count": len(open_problems)}

class ResolveRequest(BaseModel):
    problem_id: str

@app.post("/problems/resolve")
def resolve_problem(req: ResolveRequest, user: dict = Depends(verify_auth)):
    world_model.resolve_problem(req.problem_id)
    return {"status": "resolved", "problem_id": req.problem_id}
