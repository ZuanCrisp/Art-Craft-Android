# Setup - Art Craft Android Sync

Destination: `ZuanCrisp/Art-Craft-Android` (empty repository). Local folder: `D:\Vibe Coding Project\Art Craft Android`.
Nothing runs automatically: every app has its own workflow that you start by hand.

## 1. Prerequisites
- Git for Windows. Optional: GitHub CLI `gh` (`gh auth login`) so the secret, default branch and first run are automatic.
- The destination repository must be **empty** (no README, LICENSE, .gitignore).
- Your GitHub **noreply** email (GitHub > Settings > Emails, looks like `12345678+ZuanCrisp@users.noreply.github.com`).
- ONE fine-grained PAT, limited to `Art-Craft-Android`: Contents: Read and write, Workflows: Read and write, Metadata: Read.
  It is stored as the single secret `GH_SYNC_ZUZU` (same name as in your GitSync v4.7.x).

## 2. Install (the easy way)
1. Extract the zip anywhere (e.g. `D:\art-craft-android-sync`). The work folder must be empty or a clean clone.
2. Open PowerShell:
```powershell
cd D:\art-craft-android-sync
.\Start-Here.ps1 -Plan      # read-only rehearsal: checks everything, changes nothing
.\Start-Here.ps1            # real install: asks for the noreply email, then (with gh) the PAT
```
`Start-Here.ps1` fills in your path, repository and name. Without `gh`, add the secret by hand:
repository > Settings > Secrets and variables > Actions > New repository secret > name `GH_SYNC_ZUZU`.

It pushes two branches without force: `capcraft` (seed, pushed first so it becomes the default) and `art-craft-control`
(manifest, engine, docs, tests, state). A non-empty destination is refused unless you use the installer's `-AdoptExisting`.

## 3. Run syncs (on GitHub, not in PowerShell)
Actions > **Sync CapCraft** first (it turns `capcraft` into the real mirror and installs all workflows), then any other
**Sync <App>** one at a time, or **Sync ALL apps (manual)**. Tick `dry_run` for a plan-only run. Keep "Use workflow from" = `capcraft`.
Note: running **Sync CapCraft** rebuilds the `capcraft` branch, so a workflow file you added by hand there disappears.

## 4. Configuration (branch `art-craft-control`, file `config/apps.json`)
- `release_policy.initial_release_window` (default 2): first sync mirrors only the newest N releases per app; later runs add
  every new release and never remove what is already mirrored. `null` = all releases.
- `tag_policy.range` (default `1-ALL`) and per-app `tag_range`: `1-10`, `1-1000` or `1-ALL`, newest first in natural version
  order (v1.10.0 > v1.9.0). Tags needed by a mirrored release are always included. Per-app `sync_tags: false` = release tags only.
- `enabled`, `auto_sync` (only affects "Sync ALL"), `sync_prereleases`, `sync_releases`, `sync_source_default_branch`.
Update the controller later with `.\Start-Here.ps1 -UpdateControl` (keeps your edited `apps.json`; non-force).

## 5. Licences
`capcraft-android` is AGPL-3.0; the other six are Apache-2.0. The mirror keeps upstream LICENSE/NOTICE files untouched.
The organisation describes itself as an unofficial ArtCraft project; check each repository's README for name/logo restrictions
before making the mirror public.
