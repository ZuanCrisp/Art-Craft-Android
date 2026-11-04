# Art Craft Android (mirror)

This repository mirrors the open-source repositories below. Each one lives on its own branch;
this default branch (`capcraft`) mirrors CapCraft.

| Application | Branch | Upstream |
|---|---|---|
| CapCraft | `capcraft` | https://github.com/artcraft-android/capcraft-android |
| ProCraft | `procraft` | https://github.com/artcraft-android/procraft |
| LightCraft | `lightcraft` | https://github.com/artcraft-android/lightcraft-android |
| PdfCraft | `pdfcraft` | https://github.com/artcraft-android/pdfcraft-android |
| FilmCraft | `filmcraft` | https://github.com/artcraft-android/filmcraft-android |
| GridCraft | `gridcraft` | https://github.com/artcraft-android/gridcraft-android |
| WordCraft | `wordcraft` | https://github.com/artcraft-android/wordcraft-android |

- To sync one application: Actions > "Sync <App>" > Run workflow (manual only; nothing runs automatically).
  "Sync ALL apps (manual)" runs every enabled app with auto_sync=true.
- Tags and releases are mirrored with the application slug as prefix, e.g. `procraft--v1.0.0`.
- Per-application latest stable/prerelease: see `SYNC-INDEX.md` on the `art-craft-control` branch.
- Upstream GitHub Actions workflows are archived under `.upstream-archive/` and are not executed.
- Licences, NOTICE and attribution files are the upstream originals (they differ per application).

Maintained by the sync controller on branch `art-craft-control`.
