# Handoff for ChatGPT: Art Craft Android Sync (Claude and ChatGPT working together)

> Ringkasan (Bahasa Indonesia): sistem ini meng-mirror 7 repo dari org GitHub `artcraft-android` ke `ZuanCrisp/Art-Craft-Android`
> (branch default `capcraft`), dibuat Claude berdasarkan Craft Suite Sync dan dipengaruhi GitSync v4.7.2 milik pemilik. Pemilik menulis
> dalam Bahasa Indonesia: balas dalam bahasa yang sama. Jangan mengklaim "sudah dites" kalau tidak benar-benar dijalankan.

## 1. Goal and owner's wishes
Mirror `artcraft-android/{capcraft-android, procraft, lightcraft-android, pdfcraft-android, filmcraft-android, gridcraft-android,
wordcraft-android}` into one user-owned repo. One branch per app (upstream default branch, renamed to slug: capcraft, procraft,
lightcraft, pdfcraft, filmcraft, gridcraft, wordcraft), prefixed tags, newest releases with assets, per-app catalog. The destination
default branch is `capcraft`. The project is temporary ("suka-suka"). Owner's local folder: `D:\Vibe Coding Project\Art Craft Android`.
Owner's existing script GitSync v4.7.x (made with ChatGPT) must not be modified; it uses ONE secret named `GH_SYNC_ZUZU`, which this
package also uses. Make pushing to the owner's account easy: `Start-Here.ps1`.

## 2. Layout
```
Start-Here.ps1  Install-ArtCraftAndroid.ps1   (PowerShell 5.1/7; never executed by the author)
config/apps.json  engine/craft_suite/{common,manifest,gitsync,releases,catalog,cli}.py  (Python stdlib)
workflow/app-sync.yml (template -> sync-<slug>.yml per app)  workflow/sync-all.yml  templates/SYNC-INFO.md
tests/ (49 offline tests, mock GitHub API)  docs/
```
Destination branches: default `capcraft` (mirror + workflows), one per other app, and `art-craft-control` (manifest, engine, state,
`SYNC-INDEX.md`). The engine always runs from the control branch. Workflows are `workflow_dispatch` only.

## 3. Design decisions (keep unless the owner changes them)
- Pure git plumbing in a throw-away bare repo; fetch only the default branch and the selected tags into `refs/craft-suite/<slug>/...`;
  explicit `+sha:ref` pushes; never `--mirror`/`--all`.
- Upstream `.github/workflows/*` and `dependabot.yml` are archived under `.upstream-archive/` in ONE deterministic child commit
  (fixed identity/date => same SHA every run). Tags whose commit has workflows point at a sanitised child commit with metadata.
  Annotated tags keep their original object. (Rationale: tag/release events could otherwise start upstream workflows; unproven live.)
- Releases: identity = hidden marker with app slug + upstream release id; draft -> verified upload (size + SHA-256) -> publish;
  `make_latest:"false"`; release API calls use `GITHUB_TOKEN`; the PAT `GH_SYNC_ZUZU` is for `git push` only, scoped to the destination
  URL via `GIT_CONFIG_*` env. Assets are replaced when their digest differs; downloads retry 5x then fall back to the API endpoint.
- **Release window:** `release_policy.initial_release_window` (default 2). First sync = newest N releases; all current upstream
  ids go to `seen_release_ids`; later runs add every unseen release and keep the rest; nothing mirrored is removed.
- **Tag range (from GitSync v4.7.2):** `tag_policy.range` / per-app `tag_range` = `1-N` or `1-ALL`, natural version order (port of
  `Compare-NaturalTagNames`, not semver-aware); `sync_tags:false` = only tags needed by mirrored releases; those are always included;
  tags are never deleted; tags gone upstream are only reported as stale.
- No pruning anywhere; one failing app/release never blocks others; idempotent state (no per-run verbs persisted => no-op runs make no commit).
- `app=all` in "Sync ALL" = enabled && auto_sync apps; a per-app workflow ignores auto_sync.

## 4. Verified vs NOT verified
Verified offline (49 tests: git engine incl. tag range/natural order, release engine on a mock API, release window, manifest/plan,
catalog, workflows' triggers, end-to-end CLI with local repos): see `VALIDATION-RESULTS.md`.
NOT verified: both PowerShell scripts (never run), real GitHub Actions, `GITHUB_TOKEN` release/upload permissions, asset `digest`
field, that sanitised tags/releases do not start workflows, Git LFS, rate limits, upstream 504s seen earlier on the sibling project.

## 5. Notes from reading GitSync v4.7.1.1 / v4.7.2 (not modified)
Good: single secret, public-only upstream intent, noreply commit identity, provider detection, tag range, LFS toggle.
Concerns found by reading (unrun): `actions/checkout` with `persist-credentials: true` and the PAT likely sends the token to every
`github.com` URL including GitHub upstreams; assets skipped by name only; release created before assets, no `make_latest`; force-pushes;
hourly default cron. Treat as review findings, not as proven bugs.

## 6. Rules for any collaborator
1. Read this file and the code first; no wholesale rewrites; keep config/code/workflows/docs separate.
2. Never print or log secrets; never send the destination PAT to upstream hosts; no write token for reading upstream.
3. Never `push --mirror`/`--all`; force-push only managed refs (app branches, default branch, `<slug>--*` tags).
4. Do not run or build upstream code. Pruning stays off by default. Reruns must be idempotent.
5. Do not claim "tested" unless run; flag unverified API behaviour. Do not help evade platform enforcement; keep footprint small
   (manual runs, small windows, low parallelism). Owner reads each platform's Terms of Service.
6. Keep explanations short, in Indonesian, one question at a time.

## 7. Suggested work for ChatGPT
Independent review of `engine/craft_suite/*.py` and both PowerShell scripts (line by line, bugs/security/edge cases by severity);
verify the workflow YAML against current GitHub docs; propose a GitLab destination writer if the owner wants one. Return findings
as a list or a diff against the zip.

Prompt to paste: "Read docs/HANDOFF-CHATGPT.md and all files. Act as an independent reviewer: list bugs, security issues and edge
cases in engine/craft_suite/*.py, Install-ArtCraftAndroid.ps1 and Start-Here.ps1 by severity with file/line, flag every unverified
assumption, and do not claim anything is tested unless you ran it. Reply in Indonesian."
