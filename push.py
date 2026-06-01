# Github Pushing 
# 6/1/26

import subprocess
import sys
import os
from datetime import datetime

GITHUB_USERNAME = "LoganAugustine"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "WebsitePortfolio"
REPO_PATH = "/Users/lugan/Projects/WebsitePortfolio"

def git_push():
    if not GITHUB_TOKEN:
        print("No GitHub token found. Run: export GITHUB_TOKEN=your_token")
        sys.exit(1)

    commit_message = f"Site update - {datetime.now().strftime('%B %d, %Y %I:%M %p')}"
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO}.git"

    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push", remote_url, "main"]
    ]

    for cmd in commands:
        result = subprocess.run(cmd, cwd=REPO_PATH)
        if result.returncode != 0:
            print(f"Error running: {' '.join(cmd)}")
            sys.exit(1)

    print(f"Successfully pushed: '{commit_message}'")

if __name__ == "__main__":
    git_push()