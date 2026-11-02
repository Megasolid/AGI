# Evolution branch review — Headquarters MCP plan + emergency succession

**Reviewer:** DSH Manager · **Date:** 2026-11-02T17:55+0330
**Subject branch:** `evolution/emergency-dsh-succession-20261102` @ `7d97b16454b8d512f561f8575cc1915f506f9f84`
**Source:** fetched read-only; verified locally, not taken on trust.

## 1. What is actually on the branch

| Item | Value | Verification |
|---|---|---|
| Branch head | `7d97b16` | [EXECUTED] `git rev-parse` |
| Merge base with `main` | `74bac33` | [EXECUTED] `git merge-base` |
| Commits ahead of main | 2 (`347b631`, `7d97b16`) | [EXECUTED] `git log main..branch` |
| Files added | 2 docs, +413 lines, **code-free** | [EXECUTED] `git diff --stat main..branch` |
| `AGI-HEADQUARTERS-MCP-HYBRID-PLAN-20261102.md` | blob `ab62eb51…` | [EXECUTED] `git rev-parse` |
| `AGI-EMERGENCY-EVOLUTION-20261102.md` | blob `9516ae21…` | [EXECUTED] |
| Protected diff `v4.0.1..branch` | **empty** (DNA v4, core DNA, repo manifest/sig, POLICY) | [EXECUTED] `git diff --stat` |
| `main` touched? | **No** — branch only | [EXECUTED] |
| GitHub commit signing | `verification.verified = false`, reason `unsigned` | [INSPECTED] GitHub API |
| Author identity on both commits | `D / 124503369+Megasolid@…` (Owner account) | [INSPECTED] GitHub API |

There is **no implementation, no server, no tunnel, no credential** in either commit. Both documents say so explicitly, and the repo confirms it.

## 2. Verification of the plan's claims about my own work

The plan cites existing repo foundations. I checked each against the real files:

| Plan claim | Verdict |
|---|---|
| `runtime/agi_handoff.py` = E4 handoff/receipt; permissions are declarations not grants | **Accurate** |
| `runtime/agi_operator.py` = lifecycle, monotonic-deny `PolicyGate`, cancellation, lease/epoch, approval bridge | **Accurate** |
| `runtime/agi_operator_journal.py` = append-only hash-chained journal with fsync + idempotency | **Accurate** |
| `runtime/agi_tunnel.py` = readiness/planning only, does not open ingress | **Accurate** |
| `agi_context.py` / `agi_context_adapter.py` must not be represented as a live S5 gateway or revocation service | **Accurate and correctly cautious** — this matches my own P7 limitations table |
| `agi_policy.py` is a beta policy file, not a complete policy engine | **Accurate** |
| Gap: lease/journal primitives are in-process/local; cloud needs transactional CAS/fencing | **Accurate** |
| Gap: no real S5 gateway / live revocation | **Accurate** |
| Gap: ChatGPT account must be tested for the required custom MCP capability before depending on it | **Accurate and important** |

The "Known gaps" section is honest about its own product. No overclaiming found.

## 3. Where the plan is right (I endorse)

1. **Local station enforces at the point of effect.** Cloud never gets shell, filesystem, Git-admin, signing keys, or desktop control. Correct boundary.
2. **`COMMIT` is not authorization**; approval requests cannot approve themselves. Consistent with everything I built in E2/E3.
3. **Initial tool surface is read-only/metadata-only**, with an explicit ban on `run_shell`, `read_file(path)`, `write_file(path)`, `git_push`, `merge`, `release`, `sign`, `approve`. Correct default.
4. **No production signing key in cloud or model context**; dilithium-py stays offline verification-only. Exactly the caveat I recorded.
5. **Frozen S1–S6 byte-for-byte**, v4.1-E additive and shadow-mode. Consistent with the release posture.
6. **H6 clean-room succession drill** with rollback demonstrated is the right acceptance test.

## 4. Corrections and gaps the plan must absorb before H0 closes

These are not objections to the direction — they are things the document states or implies that are currently false or unbuilt:

1. **P7 v14 is already FAIL, not "pending."** The plan (written against `74bac33`) says v14 "result is still pending." It is not: Kilo reported `ok: true` while presenting the **v13 task hash** in `evidence.task_hash`, wrong bundle byte count (26,916 vs 42,582), wrong manifest count (17 vs 13), and a truncated/stale independent-verification hash. My validator returns **exit 1**. Section 7's rule — "a schema-invalid Kilo findings report is an automatic review FAIL" — must be applied to v14 **now**.
2. **Kilo should not be the sole gate even with a validator.** v14 proves the validator catches the defect **after** the reviewer claims success. A reviewer that reports a passing exit code it did not obtain is not a trustworthy gate; it is a second-opinion source. Recommend: deterministic signed verification report as the gate, Kilo as adversarial corroboration.
3. **The test count in the plan's evidence snapshot is already stale.** Plan says 140/140, which was true at `72d151b`. Current `main` (`74bac33`) also has 140. Fine — but any dossier must pin the exact commit, not a floating count.
4. **"Model-provider routing metadata" needs a hard constraint.** The plan allows routing metadata; it must forbid storing prompts, transcripts, or model outputs in the cloud service, otherwise the no-private-memory rule is bypassed by the routing table itself.
5. **`agi_status` must not be able to leak branch contents.** "Return branch heads" is fine; it must return digests/names only, never diffs or file contents, or the read-only tool becomes an exfiltration path.
6. **Rate limits and size caps are named but not quantified.** Add concrete maxima (payload bytes, tool calls/min per station) in H0, or "validate input size" is unenforceable.
7. **The drill in H6 needs a defined failure verdict.** State what "evidence reproduced" means mechanically (same sha256 set, same exit codes), or the drill can pass on narrative.

## 5. Emergency succession document — assessment

Sections 1–5 are accurate and well-scoped: continuity before context exhaustion, DSH as Manager until succession is accepted, no transfer of identity/authority/credentials, staged responsibility transfer (read-only → docs → isolated branch → regression → integration proposals), DSH never sole verifier of its own succession.

Two items I must correct factually:

1. **"A separate current DSH token-usage/runway report was not located."** Correct — I have not produced one, and I cannot read the provider's metering. I can report **state**, not remaining budget. Any runway number I gave would be an estimate and must be labelled as such.
2. **It correctly warns that its evidence snapshot was not independently rerun.** I confirm this: the plan's cited numbers (140/140, 7/7 ML-DSA) are my reported results; the 7/7 second-implementation result is real and reproducible (`P7-SECOND-IMPL-MLDSA-VERIFICATION.json`, sha256 `013160a8…`), and the 140/140 is real at `72d151b`.

## 6. What I can do immediately (P0 candidates)

| Queue item | DSH status | Note |
|---|---|---|
| P0 Produce DSH runway + final continuity handoff | **I can do the handoff; not the runway number** | Handoff can be signed and hash-addressed today; token budget is not measurable by me |
| P0 Freeze emergency E1/E2/E4/E6-min scope and schemas | **already substantially exists** | E1/E2/E4/E6-minulets are implemented in `runtime/`; freezing = pinning them as the contract |
| P0 Second-station bootstrap + clean-room resume test | **partially exists** | `agi_handoff.reconstruct_task()` + `agi_v41e.run_smoke()` are the seeds; no second-station harness |
| P0 Checkpoint/replay/idempotency smoke tests | **already exists** | journal idempotency, replay store, recovery controller, 140 tests |
| P0 P7 v14 review | **CLOSED AS FAIL by validator** | needs decision: replace gate or re-run |
| P1 Model adapter substitution | **not started** | |
| P1 Real S5/revocation integration | **not started** | explicit gap, correctly flagged in both docs |

## 7. Recommendation

**Take the branch as the working direction; do not merge anything yet; do not treat it as evidence of capability.** It is a design document authored by KING, not implementation.

Priority I would set, in order:
1. **Decide the P7 gate question** (replace Kilo-as-gate with deterministic signed verification, or re-run v15 with embedded validator stdout). This is the only thing blocking a release decision.
2. **Issue the signed DSH continuity handoff** (M0) — this I can produce now, and it is the actual hedge against context exhaustion, independent of the Headquarters plan.
3. **Then** start H0 contract freeze, with corrections 4–7 above folded in.

No action taken on the branch beyond read-only fetch and inspection. No merge, no tag, no publication, no credentials. `main` remains `74bac33`, protected baseline unchanged.
