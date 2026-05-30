# ObsidianHub

**Self-hosted, Git-backed sync for Obsidian vaults — built for teams, multiple devices, and anyone who doesn't want to pay for Obsidian Sync.**

---

## Why This Exists

Obsidian is great for writing documentation. But once you move past a single-device setup, things get complicated.

- Obsidian Sync costs money per user, and that adds up fast for teams.
- There's no built-in version control or backup.
- Sharing a vault across multiple people usually means passing files around or relying on a cloud drive that doesn't handle conflicts well.
- Some documentation contains internal or sensitive data — you might not want that sitting on a third-party sync service.

This project solves those problems with a straightforward approach: **Git as the sync engine, Obsidian as the UI, and optional S3 storage for secure cloud backup.** No monthly fees per user. No vendor lock-in. Just your notes, version-controlled and synced however you want.

---

## How It Works

```
Obsidian (write/edit docs)
       │
       ▼
  Git repo (source of truth)
       │
       ├── Syncs across devices via push/pull
       ├── Tracks every change with version history
       └── Optional push to S3 for secure cloud backup
```

The workflow is simple:

1. You write documentation in Obsidian — one file, one folder, one vault.
2. That vault is a Git repository. Every change gets committed and pushed.
3. Other devices or team members pull the latest changes.
4. Optionally, everything is backed up to S3 for encrypted cloud storage.

No daemons. No file watchers. No SaaS subscription. Just Git doing what Git does best.

---

## Architecture

| Layer | What it does |
|-------|-------------|
| **Obsidian** | The editor and UI. Everyone on the team uses Obsidian to read and write documentation. No CLI needed for day-to-day work. |
| **Git** | The synchronization layer. Tracks every change, handles merges, and acts as the source of truth. |
| **S3 (optional)** | Secure remote storage. Recommended when documentation contains sensitive or internal data. Provides encrypted, versioned backups. |
| **Python scripts** | Small automation helpers for commit/push workflows and scheduling. |

The repo folder is your vault. No symlinks, no complex setup — just point Obsidian at the folder and start writing.

---

## Features

- **Multi-device sync** — Write on your desktop, review on your laptop. Pull the latest changes on any machine.
- **Team collaboration** — Multiple people can edit the same vault. Git handles the merges.
- **Version control** — Every edit is tracked. You can see what changed, who changed it, and revert if needed.
- **Self-hosted** — No dependency on Obsidian's paid cloud. You control where your data lives.
- **S3 backend support** — Push your vault to S3 for encrypted, versioned cloud storage.
- **Secure storage** — S3 with server-side encryption and IAM policies for access control.
- **Lightweight** — A Python script, a Git repo, and optionally the AWS CLI. Nothing else.
- **Works with existing vaults** — If you already have an Obsidian vault, you can set this up in minutes without moving files around.
- **Backup-friendly** — Git history + S3 versioning means you have multiple layers of backup.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| [Obsidian](https://obsidian.md/) | Documentation editor and UI |
| [Git](https://git-scm.com/) | Version control and sync engine |
| [Python](https://python.org/) | Automation scripts for commit/push workflows |
| [AWS S3](https://aws.amazon.com/s3/) | Optional secure cloud storage |
| [AWS CLI](https://aws.amazon.com/cli/) | S3 bucket management |
| [gits3](https://pypi.org/project/git-remote-s3/) | Git transport helper for S3 remotes |

Works on **Windows**, **macOS**, and **Linux** — though this setup has been primarily tested on Windows.

---

## Installation & Setup

### 1. Install Obsidian

If you don't already have it, download Obsidian from [obsidian.md](https://obsidian.md/). Create a new vault or open an existing one. The vault is just a folder on your machine — take note of the path.

### 2. Install Git

Download Git from [git-scm.com](https://git-scm.com/). If you're on Windows, make sure to select **"Git from the command line"** during installation so it's available in your terminal.

Verify it works:

```bash
git --version
```

### 3. Initialize the Git Repository

Open a terminal in your vault folder:

```bash
cd /path/to/your/vault
git init
git add .
git commit -m "Initial commit"
```

That's it. Your vault is now a Git repository. Every note you write can be tracked and versioned.

### 4. Add a Remote Repository

To sync across devices or share with a team, you need a remote. This can be GitHub, GitLab, your own server, or an S3 bucket.

**Using GitHub:**

```bash
git remote add origin https://github.com/your-username/your-vault.git
git branch -M main
git push -u origin main
```

**Using your own Git server (SSH):**

```bash
git remote add origin ssh://user@your-server.com:/path/to/repo.git
git push -u origin main
```

**Using S3 (see next section):**

### 5. Configure S3 Backend (Optional)

If your documentation contains sensitive information — internal architecture docs, infrastructure notes, compliance records — S3 is a good option. You get encryption, versioning, and full control over access.

**Step 1: Install and configure the AWS CLI**

Download from [aws.amazon.com/cli](https://aws.amazon.com/cli/). Then:

```bash
aws configure
```

You'll need an **Access Key ID** and **Secret Access Key** from an IAM user with S3 permissions. The IAM policy should at minimum allow:

- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`

**Step 2: Create an S3 bucket**

```bash
aws s3 mb s3://your-bucket-name --region your-region
```

Enable versioning so you never lose a change:

```bash
aws s3api put-bucket-versioning \
  --bucket your-bucket-name \
  --versioning-configuration Status=Enabled
```

**Step 3: Install the S3 Git transport helper**

Git needs a helper to push to S3. Install it via pip:

```bash
pip install git-remote-s3
```

**Step 4: Link your repo to S3**

```bash
git remote add origin s3://your-bucket-name/vault-backup.git
git push -u origin main
```

A few notes on S3:
- Storage costs about $0.023/GB/month. A text-only vault is usually under 100 MB — less than a penny per month.
- Enable server-side encryption (SSE-S3 or SSE-KMS) for data at rest.
- S3-compatible alternatives like MinIO (self-hosted), DigitalOcean Spaces, or Wasabi also work with the same setup.

### 6. Sync Workflow

Once everything is set up, here's the daily workflow:

1. **Pull the latest changes** — If you're on a different device or someone else pushed updates:
   ```bash
   git pull origin main
   ```
2. **Write or edit notes** in Obsidian as usual.
3. **Stage and commit your changes:**
   ```bash
   git add .
   git commit -m "Updated architecture docs"
   ```
4. **Push to the remote:**
   ```bash
   git push origin main
   ```

To automate this, set up a scheduled task (Windows Task Scheduler, cron, or launchd) that runs a simple script every 30 minutes:

```python
# sync.py — minimal example
import subprocess, time

repo = "/path/to/your/vault"

def sync():
    subprocess.run("git add -A", cwd=repo, shell=True)
    result = subprocess.run("git status --porcelain", cwd=repo, capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        msg = f"auto sync {time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(f'git commit -m "{msg}"', cwd=repo, shell=True)
        subprocess.run("git push origin main", cwd=repo, shell=True)

if __name__ == "__main__":
    sync()
```

---

## Security Recommendations

If documentation confidentiality matters to your team, here are the things to get right:

- **Use S3 for sensitive documentation.** GitHub repos are convenient, but if your docs contain internal architecture, credentials, or compliance data, S3 gives you encryption and IAM policies. You control who can read and write.
- **Restrict IAM permissions.** The IAM user or role used for sync should only have permissions for the specific S3 bucket. Avoid giving blanket S3 access.
- **Enable bucket versioning.** This protects against accidental deletions or malicious changes. You can always restore a previous version.
- **Don't commit secrets to Git.** If you store API keys, passwords, or tokens in your vault, add them to a `.gitignore` file or use a dedicated secrets manager. Git history keeps everything forever — including mistakes.
- **Use private repositories.** If you go with GitHub, make the repo private. It's free.
- **Enable S3 encryption.** Either SSE-S3 (AES-256, managed by AWS) or SSE-KMS (if you need customer-managed keys). Both are straightforward to enable on the bucket.
- **Consider limiting write access.** If multiple people are pushing to the same repo, make sure only trusted users have write access to the remote.

---

## Use Cases

This setup works well for several real-world scenarios:

**DevOps documentation** — Infrastructure topology, deployment runbooks, incident response guides. Keep it versioned and accessible across the team.

**Internal team wiki** — Replace Notion, Confluence, or Google Docs with something that doesn't lock your data behind a subscription. Obsidian as the editor, Git as the storage.

**Infrastructure notes** — Server configurations, network diagrams, database schemas. The kind of documentation that needs to be accurate and up to date.

**SOP management** — Standard operating procedures that multiple team members need to reference and update. Version history means you can track changes over time.

**Engineering runbooks** — On-call runbooks, escalation procedures, debug workflows. These change frequently and benefit from automated sync.

**Startup knowledge base** — Early-stage companies that need documentation but don't want to spend on premium tools. This costs essentially nothing to run.

**Multi-device personal notes** — One person, multiple machines. Write on your work laptop, reference on your personal machine. No manual file transfers.

---

## Future Improvements

This is a working setup, but there's room to grow. Some things on the roadmap:

- **Automated background sync** — Replace the scheduled script with a lightweight daemon that watches for file changes and syncs immediately.
- **Web dashboard** — A simple UI to view commit history, manage vaults, and check sync status.
- **Access control management** — Fine-grained permissions for who can read and write specific documentation sets.
- **Encryption support** — Client-side encryption before pushing to S3 or GitHub, so data is encrypted even before it leaves your machine.
- **Docker deployment** — A containerized version of the sync agent that can run on servers or NAS devices.
- **Multi-tenant support** — Host documentation for multiple teams from a single backend, with isolated vaults.
- **Desktop sync agent** — A small system tray application that shows sync status and provides manual sync controls without opening a terminal.

---

## Project Structure

```
ObsidianHub/
├── sync.py            # Automation script for commit/push
├── syncDocs.py        # Extended version with logging
├── git_sync.log       # Sync activity log (generated)
├── log.txt            # Human-readable history (generated)
└── README.md          # This file
```

---

## License

MIT. Use it, modify it, share it. If you build something useful on top of it, that's great — but there's no obligation.