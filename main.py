"""
EPOCH entry point.
Run as autonomous agent: python main.py
Run as API server:       uvicorn api.main:app --reload
"""
import sys
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "agent"

    if mode == "agent":
        from core.agent import EpochAgent
        agent = EpochAgent(interval_seconds=60)
        agent.run()

    elif mode == "once":
        from core.agent import EpochAgent
        agent = EpochAgent()
        report = agent.run_once()
        import json
        print(json.dumps(report, indent=2, default=str))

    elif mode == "api":
        import uvicorn
        uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
