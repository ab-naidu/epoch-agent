# EPOCH — Autonomous Predictive Agent

> It doesn't wait for problems. It finds them before they exist, and fixes them before you notice.

EPOCH is a fully autonomous agent that observes your systems, builds a live world model, simulates future failures, and acts — with zero human prompts.

## How it works

```
Observe → Model → Simulate → Plan → Execute → Escalate → Learn
   ↑                                                         ↓
   └─────────────────── continuous loop ────────────────────┘
```

1. **Observe** — ingests live signals from GitHub, infrastructure, and data sources via Airbyte
2. **Model** — builds a real-time world model stored in Aerospike
3. **Simulate** — AWS Bedrock reasons forward: "what breaks in the next 72 hours?"
4. **Plan** — generates autonomous action plans, no human goal required
5. **Execute** — opens GitHub issues/PRs, triggers API workflows
6. **Escalate** — calls your on-call engineer via Bland AI when human judgment is needed
7. **Learn** — updates world model based on outcomes

## Sponsor integrations

| Sponsor | Role |
|---|---|
| AWS Bedrock | Forward simulation reasoning engine |
| Aerospike | Real-time world model + problem memory |
| Airbyte | Live data ingestion from any source |
| Auth0 | Identity + scoped permissions for every action |
| Bland AI | Voice escalation to humans |
| TrueFoundry | Full observability on every reasoning trace |
| Kiro | Spec-driven development, hooks, steering docs |

## Quickstart

```bash
git clone https://github.com/ab-naidu/epoch-agent
cd epoch-agent
pip install -r requirements.txt
cp .env.example .env
# fill in your API keys

# run one cycle
python main.py once

# run continuously
python main.py agent

# run as API server
python main.py api
```

## API endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /health | none | Agent status |
| POST | /agent/start | none | Start autonomous loop |
| POST | /agent/run-once | Auth0 | Trigger single cycle |
| GET | /world-model | Auth0 | Current world state |
| GET | /problems | Auth0 | All detected problems |
| GET | /problems/open | Auth0 | Unresolved problems |
| POST | /problems/resolve | Auth0 | Mark problem resolved |

## Hackathon

Built at the **Deep Agents Hackathon** hosted at AWS Builder Loft on March 27, 2026.

This project was conceived, designed, and built in a single day as part of the hackathon challenge:
> "Build agents that plan, reason, and execute across complex multi-step tasks autonomously."

EPOCH was my submission — an autonomous predictive agent that requires zero human prompts to operate. It observes your systems, reasons about what will break next, and acts before you even know there's a problem.

Devpost: https://devpost.com
GitHub: https://github.com/ab-naidu/epoch-agent

Built by: [@ab-naidu](https://github.com/ab-naidu)
