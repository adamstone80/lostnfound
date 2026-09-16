# Deployment notes

This app is synced across three places:

- **Local machine** — this git repo
- **GitHub** — `adamstone80/lostnfound`, branch `main`
- **Replit** — workspace imported from GitHub, deployed at `https://lostnfound--adamjulianstone.replit.app` on a Reserved VM

Replit uses `uv` for dependencies (`pyproject.toml` + `uv.lock`), separate from the `web-requirements.txt` used for local pip installs.

## Getting changes live

Pulling code into Replit is **not** the same as deploying it. Two separate steps are required:

1. In the Replit **Shell**, run:
   ```
   git pull --no-rebase origin main
   ```
2. In the Replit UI, click **Deploy → Redeploy**.

A `git pull` alone updates the workspace but does not touch the live `.replit.app` URL.

## Why Reserved VM, not Autoscale

Autoscale deployments are stateless — instances don't share a filesystem and disks reset on restart/redeploy. This app stores its SQLite database (`data.db`) and uploaded photos on local disk, so Autoscale would silently lose data. Reserved VM runs one persistent instance with a persistent disk, which is safe for this setup.

## Git authentication in the Replit shell

Plain `git push` in the Replit shell fails with "Invalid username or token" even when Replit's own GitHub integration is connected, because that integration isn't wired into the shell's git credential helper. Fix once per Repl:

```
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

## Resolving divergent branches

Replit's own Agent periodically auto-commits directly in the workspace (environment config, scaffolding changes) independent of anything pushed from GitHub. When `git pull` reports divergent branches, don't force-overwrite either side. Inspect first:

```
git log --oneline -5
git show <hash> --stat
```

So far, every divergence has turned out to be non-overlapping additions (e.g. both sides adding different blocks to `.replit`) rather than real conflicts — merge with `git pull --no-rebase origin main` and keep both blocks when a conflict marker appears, unless the two sides genuinely contradict each other.
