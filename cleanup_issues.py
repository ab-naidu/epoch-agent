"""
Close all duplicate GitHub issues, keep only the latest clean ones.
"""
import requests, os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# Get all open issues
r = requests.get(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100", headers=headers)
issues = r.json()
print(f"Found {len(issues)} open issues")

# Close all except the last 3 clean [EPOCH] ones
epoch_issues = [i for i in issues if i["title"].startswith("[EPOCH]")]
other_issues = [i for i in issues if not i["title"].startswith("[EPOCH]")]

# Close all "EPOCH detected issue" blanks and duplicates
to_close = other_issues + epoch_issues[3:]  # keep top 3 newest [EPOCH] issues

for issue in to_close:
    requests.patch(
        f"https://api.github.com/repos/{repo}/issues/{issue['number']}",
        headers=headers,
        json={"state": "closed"}
    )
    print(f"Closed #{issue['number']}: {issue['title']}")

print("\nDone. Remaining open issues:")
r2 = requests.get(f"https://api.github.com/repos/{repo}/issues?state=open", headers=headers)
for i in r2.json():
    print(f"  #{i['number']}: {i['title']}")
