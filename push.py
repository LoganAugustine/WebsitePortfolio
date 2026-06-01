# Github Pushing 
# 6/1/26

import subprocess
import sys
from datetime import datetime

def git_push():
    # Auto-generates a commit message with the current date and time
    commit_message = f"Site update - {datetime.now().strftime('%B %d, %Y %I:%M %p')}"
    
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push"]
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, cwd="/Users/lugan/Projects/WebsitePortfolio")
        if result.returncode != 0:
            print(f"Error running: {' '.join(cmd)}")
            sys.exit(1)
    
    print(f"Successfully pushed: '{commit_message}'")

if __name__ == "__main__":
    git_push()