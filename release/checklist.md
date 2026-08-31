# Release checklist — `se-agent` v`X.Y.Z`

Publish a new `se-agent` release by walking the six steps below in order. Steps 1–4 are automated-verifiable; step 5 is manual and currently **BLOCKED**; step 6 records the standing non-goals that must never be violated by this process. First release version is `0.1.0` (tag `v0.1.0`); renumbering before first publication is allowed.

## Quick path

1. Verify CI green on `main` with empty before/after status snapshots, and payload sync idempotency.
2. Confirm `pyproject.toml` version == intended `X.Y.Z`.
3. Create and push annotated tag `vX.Y.Z` (tag protection recommended).
4. Verify the CI `version-tag` job passes.
5. (MANUAL, BLOCKED) pipx install from the real tag ZIP and offline smoke test.
6. Confirm non-goals: no manifest, no hashes, no generated outputs committed.

## Step 1 — CI green on `main` with read-only evidence

- [ ] Latest GitHub Actions run on `main` (`.github/workflows/ci.yml`, `test` job) is green.
- [ ] The job log records the read-only evidence: `working-tree-clean before: OK/empty` and `working-tree-clean after: OK/empty` — both full-status snapshots (`git status --porcelain=v1 --untracked-files=all --ignored=matching`) captured empty, diff empty (AC-11).
- [ ] Payload mirror sync idempotency (local dev): run `python tools/sync_payload.py` twice; the second run leaves `git diff` empty. `tools/sync_payload.py` is never run by CI — CI only verifies mirror equality.

## Step 2 — Version equality

- [ ] `pyproject.toml` `[project] version` equals the intended `X.Y.Z` (single source of truth; printed `--version` equals it by construction via installed metadata).

## Step 3 — Annotated tag

- [ ] Create the annotated tag on the release commit: `git tag -a vX.Y.Z -m "se-agent X.Y.Z"` and push it: `git push origin vX.Y.Z`.
- [ ] Recommended repo-level protection: tag protection / immutable tags for `v*` so published tags never move.

## Step 4 — CI version-tag job

- [ ] On the tag push, the `version-tag` job (trigger: `refs/tags/v*`) passes: it compares `${GITHUB_REF_NAME#v}` against the `pyproject.toml` version and fails on any mismatch (automated half of AC-2). No build, install, or pytest in this job.

## Step 5 — MANUAL AC-1/AC-2: pipx install from the real tag (BLOCKED)

> **BLOCKED by the open GitHub organization/URL placeholder follow-up** (`https://github.com/<organizacion>/<repo>`). Do not execute this step until the real URL exists; this placeholder blocks only this step.

On a clean machine:

- [ ] `pipx install https://github.com/<organizacion>/<repo>/archive/refs/tags/vX.Y.Z.zip` succeeds.
- [ ] `se-agent --version` prints exactly `X.Y.Z` (no `v` prefix) and exits 0; tag `vX.Y.Z`, `pyproject.toml` version, and printed version are all equal.
- [ ] `se-agent init --harness codex --target /tmp/scratch` into an empty scratch directory succeeds; the tree contains exactly the write-set expansion and nothing else (no `.framework-agent/`, no manifest, no caches).
- [ ] Offline check: with no network connectivity, `init` completes without attempting or requiring any network I/O (the payload travels inside the installed package).

## Step 6 — Non-goals (standing constraints)

- [ ] No manifest and no SHA-256 hashes are produced by this process (PRD non-goals; the tool leaves no residual state).
- [ ] `release/` holds only sources (this checklist, future notes); generated outputs stay in `dist/` — gitignored, local dev only. CI builds into `$RUNNER_TEMP`, never into the checkout, and no build artifact is ever committed.
