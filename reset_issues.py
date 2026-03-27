"""
Close ALL issues and create 3 clean demo-ready ones.
"""
import requests, os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# Close everything
r = requests.get(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100", headers=headers)
for issue in r.json():
    requests.patch(f"https://api.github.com/repos/{repo}/issues/{issue['number']}", headers=headers, json={"state": "closed"})
    print(f"Closed #{issue['number']}")

# Create 3 clean issues
clean_issues = [
    {
        "title": "[EPOCH] Database query degradation — outage risk in 48h",
        "body": "## EPOCH Autonomous Detection\n\n**Category:** performance\n**Severity:** 9/10\n**Probability:** 87%\n\n### Description\nSlow query count has grown 4x in 6 hours. At current growth rate, the database will hit connection limits within 48 hours causing a full service outage.\n\n### Predicted Impact\nFull service outage affecting all users. Estimated downtime: 2-4 hours.\n\n### Suggested Action\nAdd index on `users.created_at`, optimize top 3 slow queries identified in query logs, consider read replica for reporting queries.\n\n---\n*Detected autonomously by EPOCH — no human prompt required.*",
        "labels": ["epoch-agent", "critical"]
    },
    {
        "title": "[EPOCH] Security — unsigned commits detected on main branch",
        "body": "## EPOCH Autonomous Detection\n\n**Category:** security\n**Severity:** 7/10\n**Probability:** 100%\n\n### Description\nRecent commits to main branch are missing GPG signatures. This violates security policy and could indicate unauthorized code changes.\n\n### Predicted Impact\nPotential supply chain attack vector. Compliance violation if audited.\n\n### Suggested Action\nEnable required commit signing in branch protection rules. Notify team to configure GPG keys.\n\n---\n*Detected autonomously by EPOCH — no human prompt required.*",
        "labels": ["epoch-agent", "high"]
    },
    {
        "title": "[EPOCH] Rising error rate — service degradation imminent",
        "body": "## EPOCH Autonomous Detection\n\n**Category:** reliability\n**Severity:** 8/10\n**Probability:** 92%\n\n### Description\nError rate has increased from 0.1% to 4.2% over the last 3 hours. Pattern matches previous incidents that preceded full outages.\n\n### Predicted Impact\nService degradation within 6 hours. SLA breach likely if not addressed.\n\n### Suggested Action\nCheck recent deployments, review error logs for root cause, consider rollback of last deployment.\n\n---\n*Detected autonomously by EPOCH — no human prompt required.*",
        "labels": ["epoch-agent", "critical"]
    }
]

print("\nCreating clean issues...")
for issue in clean_issues:
    r = requests.post(f"https://api.github.com/repos/{repo}/issues", headers=headers, json=issue)
    print(f"Created #{r.json()['number']}: {r.json()['title']}")
