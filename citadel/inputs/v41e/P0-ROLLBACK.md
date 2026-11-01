# P0 rollback plan — v4.1-E to v4.0.1

**Status:** P0 planning artifact. No rollback executed; no release published.

## 1. Rollback target

| Item | Value |
|---|---|
| Tag | `v4.0.1` |
| Commit | `6a0fb796a624cf61fc8592aa3f45fc4dc6c10738` |
| Tree | `083f0ee27dc7368196f239175e212aa84cb039eb` |
| Runtime asset | `releases/runtime/2026-10-30/agi-runtime-v4.0.1.zip` |
| Runtime sha256 | `85a922540097315802509634a0e03e6a7940f4cf378a485fc93d2f00e85ec781` |

## 2. Preconditions

- A v4.1-E release candidate exists only as a **new tag**, never a rewrite of main history.
- No force-push, no tag rewrite, no deletion of v4.0.1.
- Frozen artifacts are byte-identical before and after any candidate.
- A rollback drill has been executed (not just documented).

## 3. Rollback steps (candidate future)

1. Stop/close the v4.1-E runtime without deleting Branch state.
2. Verify the v4.0.1 tag/commit and runtime zip hash above.
3. Reinstall/activate v4.0.1 using its published install path.
4. Boot v4.0.1; verify boot gate and core identity.
5. Verify the Branch manifest/state can be read by v4.0.1; do not run destructive migration.
6. Record the rollback event and evidence; report to KING/Owner.
7. Keep the failed candidate's evidence for diagnosis; do not delete it.

## 4. Rollback drill acceptance

- Boot v4.0.1 from the pinned asset.
- `boot_gate` PASS.
- Branch manifest verifies.
- No frozen file changed.
- Evidence packet with hashes and exact commands.

## 5. Non-authorization

Documentation only. No tag, deployment or rollback is authorized/executed by this plan.
