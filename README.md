# Art Craft Android Sync

Mirrors the 7 repositories of the GitHub organisation `artcraft-android` into `ZuanCrisp/Art-Craft-Android`:
one branch per app (upstream default branch, renamed to the app slug), prefixed tags, the newest releases with their assets,
and a per-app "latest" catalog. Default branch of the destination: `capcraft`. Manual runs only. No upstream build, script or
workflow is ever executed.

```
Start-Here.ps1               one command: installs into YOUR account (asks only for your noreply email)
Install-ArtCraftAndroid.ps1  the installer behind it (-Plan, -UpdateControl, -Repository, -SetSecret ...)
config/apps.json             manifest: 7 apps, toggles, tag range, release window
engine/                      Python (stdlib only): git engine, release engine, catalog, CLI
workflow/                    app-sync.yml (one manual workflow per app) + sync-all.yml
templates/SYNC-INFO.md       pointer README written to the default branch
docs/                        SETUP.md, OPERATIONS.md, TEST-PLAN.md, HANDOFF-CHATGPT.md
tests/                       49 offline tests + mock GitHub API
VALIDATION-RESULTS.md        what was actually run, and what was not
```
Start with `docs/SETUP.md`.
