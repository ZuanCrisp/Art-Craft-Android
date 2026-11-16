# Operations - Art Craft Android Sync

## What ends up in the destination
- Branch per app: the upstream **default branch only**, renamed to the slug (`capcraft`, `procraft`, ...). Upstream workflows
  (and `dependabot.yml`) move to `.upstream-archive/` in ONE deterministic child commit; trees without them are pushed untouched.
- Tags `<slug>--<tag>`: annotated tags keep their original object; tags whose commit contains workflows point at a sanitised
  child commit (original commit as parent). Range/selection: see SETUP section 4.
- Releases `[App] <title>`: provenance block + upstream notes + all assets; created as DRAFT, assets verified (size + SHA-256),
  then published; always `make_latest=false`.
- Catalog: `state/release-catalog.json` and `SYNC-INDEX.md` on the control branch.

## Release window
First sync of an app: only the newest N releases (default 2). Every upstream release id at that moment is recorded in
`seen_release_ids`. Later runs: every release not seen before (new versions, late backports) plus the ones already mirrored.
Nothing mirrored is removed. Older releases outside the first window are never pulled in later.

## Idempotency, assets, failures
No upstream change => no push, no API write, no state commit. Assets are skipped only when size and SHA-256 match; a changed
asset with the same name is replaced. Downloads retry 5x (5/20/60/120 s) then fall back to the API endpoint. A failed release
stays a DRAFT, the job turns red, and re-running the same workflow finishes it. One failing app/release never blocks the others.
Error categories: `DEFAULT_BRANCH_UNKNOWN`, `BRANCH_FETCH_FAILED`, `BRANCH_PUSH_FAILED`, `TAG_LIST_FAILED`, `TAG_FETCH_FAILED`,
`TAG_PUSH_FAILED`, `TAG_MAPPING_CONFLICT`, `RELEASE_LIST_FAILED`, `RELEASE_TAG_MISSING`, `RELEASE_CONFLICT`, `ASSET_DOWNLOAD_FAILED`,
`ASSET_DIGEST_MISMATCH`, `ASSET_UPLOAD_FAILED`, `LFS_UNAVAILABLE`, `LFS_TRANSFER_FAILED`, `AUTH_MISSING`, `DEST_MISMATCH`, `NO_RESULT`.

## Safety rules (unchanged)
Explicit refspecs only (never `--mirror`/`--all`); the PAT is used for `git push` only, scoped to the destination URL, never sent
to upstream; release API calls use the workflow's `GITHUB_TOKEN`; no pruning; nothing from upstream is executed.

## Known limits
Git LFS only for the default-branch tip; no pruning; "immutable releases" setting would conflict with asset replacement.
Natural tag ordering is not semver-aware (`v1.0.0-rc1` ranks above `v1.0.0`), same as GitSync v4.7.2.
