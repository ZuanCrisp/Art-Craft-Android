# Validation results

Environment: Linux sandbox, Python 3.12.3, git 2.43.0, no network, no PowerShell, no git-lfs.
Command: `python3 -m unittest discover -s tests -v` -> **Ran 49 tests, OK** (about 16 s).

## Passed (actually executed)
- Git engine, 12 tests incl. new ones: default branch `trunk` detected; only the default branch pushed and renamed; workflows archived
  with the original commit as parent; annotated tags preserved; idempotent reruns; moved/deleted tags; two apps without collisions;
  default-app overlay; dry run; auth header scoped to the destination URL; **tag range** (`1-1` keeps the newest, release tags always
  included, nothing stale that still exists upstream); **tags disabled** (release tags only, nothing deleted).
- Tag selection, 3 tests: natural order (v1.10.0 above v1.9.0), `1-N`/`1-ALL`/`1-1000`, invalid ranges rejected.
- Release engine on a mock GitHub API, 12 tests; release window, 6 tests (first sync newest 2 of 5, accumulate, backport, retry after failure,
  null window/upgrade path, dry run).
- Manifest/plan/catalog/workflows, 12 tests: 7 repos of artcraft-android, default branch `capcraft`, invalid input incl. tag range and
  default-branch checks rejected, per-app workflows + sync-all only `workflow_dispatch`, overlay carries 7 workflows + sync-all.
- End-to-end through the real CLI, 4 tests: full cycle and byte-identical rerun, wrong destination refused, failure isolation with honest
  aggregate status, dry run writes nothing, no secret in output.

## NOT verified
- `Start-Here.ps1` and `Install-ArtCraftAndroid.ps1` have never been executed (braces/brackets balance only). Run `.\Start-Here.ps1 -Plan` first.
- Everything needing real GitHub: Actions runtime, `GITHUB_TOKEN` permissions, asset `digest` field, tag/release not triggering workflows,
  Git LFS, rate limits, upstream download 504s. The 7 upstream default branches and their release assets were not inspected.
