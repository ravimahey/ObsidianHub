import os
import time
import subprocess
import logging

# -----------------------
# 📁 REPO PATH (same as script location)
# -----------------------
REPO_PATH = os.path.dirname(os.path.abspath(__file__))

# -----------------------
# 📄 LOG FILES (same folder)
# -----------------------
log_file = os.path.join(REPO_PATH, "git_sync.log")
log_txt_file = os.path.join(REPO_PATH, "log.txt")

# -----------------------
# 🔥 LOGGING SETUP
# -----------------------
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {msg}"

    print(line)

    # structured log
    logging.info(msg)

    # human-readable log
    with open(log_txt_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# -----------------------
# 🔧 GIT SYNC FUNCTION
# -----------------------
def git_sync():
    try:
        log("🔄 Sync job started")

        # add changes
        subprocess.run("git add -A", cwd=REPO_PATH, shell=True, check=True)

        # check changes
        result = subprocess.run(
            "git status --porcelain",
            cwd=REPO_PATH,
            shell=True,
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            log("No changes found")
            return

        # commit
        msg = f"auto sync {time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(f'git commit -m "{msg}"', cwd=REPO_PATH, shell=True, check=True)

        # push
        push_result = subprocess.run(
            "git push origin main",
            cwd=REPO_PATH,
            shell=True,
            capture_output=True,
            text=True
        )

        if push_result.returncode == 0:
            log("🚀 Sync successful")
        else:
            log(f"❌ Push failed: {push_result.stderr}")

    except subprocess.CalledProcessError as e:
        log(f"❌ Git command error: {e}")
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
    finally:
        log("🏁 Sync job finished")


# -----------------------
# ▶ MAIN
# -----------------------
if __name__ == "__main__":
    git_sync()