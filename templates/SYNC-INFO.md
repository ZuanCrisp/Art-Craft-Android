# __PROJECT_NAME__ (mirror)

This repository mirrors the open-source repositories below. Each one lives on its own branch;
this default branch (`__DEFAULT_BRANCH__`) mirrors __DEFAULT_APP__.

| Application | Branch | Upstream |
|---|---|---|
__APP_TABLE__

- To sync one application: Actions > "Sync <App>" > Run workflow (manual only; nothing runs automatically).
  "Sync ALL apps (manual)" runs every enabled app with auto_sync=true.
- Tags and releases are mirrored with the application slug as prefix, e.g. `procraft--v1.0.0`.
- Per-application latest stable/prerelease: see `SYNC-INDEX.md` on the `__CONTROL_BRANCH__` branch.
- Upstream GitHub Actions workflows are archived under `.upstream-archive/` and are not executed.
- Licences, NOTICE and attribution files are the upstream originals (they differ per application).

Maintained by the sync controller on branch `__CONTROL_BRANCH__`.
