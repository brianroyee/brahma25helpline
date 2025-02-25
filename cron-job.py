import os
import subprocess
import sys
#FILE_NAME = "bot_stats.json"
#PATH = "/home/ssm-user/brahma25helpline"
#JSON_PATH = os.path.join(PATH, FILE_NAME)

#os.chdir(PATH)
#os.system(f"git add {FILE_NAME}")
#os.system('git commit -m "[AWS]: Automated JSON Update"')
#os.system('git push origin main')

REPO_PATH = "/home/ssm-user/brahma25helpline"
FILE_TO_MONITOR = "bot_stats.json"
BRANCH = "main"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("token env not set")
    sys.exit(1)

os.chdir(REPO_PATH)

result = subprocess.run(["git", "diff", "--quiet", FILE_TO_MONITOR])
if result.returncode == 0:
    print("No changes detected in the JSON file. Exiting without committing.")
    sys.exit(0)

subprocess.run(["git", "add", FILE_TO_MONITOR], check=True)

subprocess.run(["git", "commit", "-m", "[AWS]: Automated JSON Update"], check=True)

push_url = f"https://{GITHUB_TOKEN}@github.com/brianroyee/brahma25helpline.git"
subprocess.run(["git", "push", push_url, BRANCH], check=True)

print("Changes pushed successfully!")
