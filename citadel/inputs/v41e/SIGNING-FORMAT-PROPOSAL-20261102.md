# Signing-format specification and key-purpose statement — for Owner decision

**Status:** proposal only. **No signature has been created; no key use is authorized by this document.**  
**Requested by:** GPT/KING review of REPORT-01 (2026-11-02T01:59).  
**Related:** `king-decision-20261102.json`, `king-decision-02-20261102.json`, `REPORT-01-planning.md`.

---

## 1. Purpose

Define the exact signature format and key purpose for v4.1-E task manifests, release manifests and evidence packets, so the Owner can approve or reject a minimal signing path without ambiguity.

## 2. Canonical payload

- Encoding: UTF-8 **NFC**.
- Canonical JSON: sorted object keys, separators `(',',':')`, no insignificant whitespace, `ensure_ascii=false`.
- Hash: SHA-256 over the canonical bytes; hex lowercase.
- This matches the existing `task_hash` convention in `citadel/README.md` and existing signed tasks.

## 3. Task signature format (`agi-citadel/task/0.2`)

Existing tasks already use this shape:

```json
{
  "schema": "agi-citadel/task/0.2",
  "task_id": "...",
  "station": "...",
  "issued_by": "...",
  "objective": "...",
  "scope": [],
  "constraints": [],
  "inputs": [{"path": "...", "sha256": "sha256:...", "hash_method": "..."}],
  "expected_report": {},
  "authorization_scope": "...",
  "human_approval_required": true,
  "hash_method": "sha256(canonical_json(task excluding task_hash and signature))",
  "signature_method": "ML-DSA-65 over utf8(canonical_json(task excluding task_hash and signature))",
  "task_hash": "sha256:...",
  "signature": {
    "schema": "agi-sig/1",
    "alg": "ML-DSA-65",
    "key_id": "a73eaa5d3c31e009",
    "public_key_b64": "...",
    "payload_sha256": "...",
    "signature_b64": "...",
    "signed_at": "..."
  }
}
```

Rules:
1. `task_hash = "sha256:" + sha256(canonical_json(task excluding task_hash and signature))`.
2. `signature.payload_sha256` equals the same canonical digest.
3. `signature.signature_b64` is ML-DSA-65 over the canonical bytes.
4. Verification: remove `task_hash` and `signature`, canonicalize, recompute hash; verify signature over those bytes with the embedded public key and expected `key_id`.
5. A task without a valid `task_hash`/`signature` is a **draft**, not an issued task.

**Tooling gap:** no dedicated `sign_task.py`/`verify_task.py` exists in the repository; existing `kilo_verify.py` verifies the hash and inputs but explicitly does **not** verify the signature. P0 must add a small deterministic signer/verifier (or use `crypto.py` primitives correctly). No task is signed until that exists and is tested.

## 4. Detached artifact signature format

For release manifests, evidence packets and other files:

```json
{
  "schema": "agi-sig/1",
  "alg": "ML-DSA-65",
  "key_id": "a73eaa5d3c31e009",
  "public_key_b64": "...",
  "payload_sha256": "<sha256 hex of raw file bytes>",
  "signature_b64": "...",
  "signed_at": "2026-11-02T..."
}
```

- Stored as `<file>.sig` next to the payload (same convention as `repo.json.sig`).
- `payload_sha256` covers the **raw bytes** of the file, not a re-canonicalized form. The manifest itself must therefore be written in the canonical form if canonicality is claimed.
- Verification: `python memory/scripts/crypto.py verify <file> --sig <file>.sig --key-id a73eaa5d3c31e009`.

## 5. Key-purpose statement

| Item | Statement |
|---|---|
| Key | ML-DSA-65 device key, `key_id a73eaa5d3c31e009` |
| Storage | DPAPI-sealed to this machine (`state/keys/device.json`, `device.key`); no HSM |
| Intended use | **DSH operational signing**: Citadel task manifests, release manifests, evidence packets, repo/trust artefacts where the existing procedure uses the device key |
| Not intended as | Owner identity, root authority, federation credential, or a substitute for an Owner decision |
| Owner authorization | Issue #6 (Owner-authored) + explicit Owner approval in project conversation; this proposal requests approval of the **key use and format**, not a new Owner signature |
| Limits | No root 2-of-3 use unless the Owner/frozen contract requires it; no key export; no signature reuse across tasks; no secret in reports/logs |
| Failure | If the key is unavailable/unsealed: stop signing; do not generate an alternate key or fabricate a signature |

## 6. Options for Owner decision

| Option | Description | Recommendation |
|---|---|---|
| **A. Device key + `agi-sig/1`** | Use the existing ML-DSA-65 device key for DSH-issued task manifests and release candidate manifests; verify with embedded public key and pinned `key_id`. | **Recommended for P0**, subject to Owner approval. Minimal, matches existing artefacts, no new key ceremony. |
| **B. Governance wrapper** | Issue #6 + KING decision records + DSH-signed task manifests; Owner retains final decision. | **Recommended alongside A**; preserves authority separation. |
| **C. Root-signed release** | ML-DSA-87 2-of-3 root signs the final release decision/manifest. | Only if Owner or frozen release policy requires it; root shards are currently local and offline move is pending. |

King's position: Option A is the preferred minimal path, but **key use and `agi-sig/1` adoption require explicit Owner approval**; do not use root 2-of-3 unless required.

## 7. Open issues to resolve in P0

1. Owner approval of key use + `agi-sig/1` format (this document).
2. `sign_task.py`/`verify_task.py` deterministic tooling and tests.
3. Task schema 0.1 vs 0.2 reconciliation.
4. Whether the final release manifest uses device key A, root C, or both.
5. GitHub operations use the `Megasolid` account credential (see REPORT-01 addendum); Owner awareness/authorization for write use.

## 8. Non-authorization

No signature was produced. This proposal does not authorize implementation, key use, repository writes, release publication, or any frozen/DNA change.
