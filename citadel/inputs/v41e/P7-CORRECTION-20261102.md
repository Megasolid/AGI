# P7 correction record — v41e-v-11 findings metadata

**Correction ID:** `P7-CORR-01`  
**Date:** 2026-11-02T12:12+0330  
**Status:** correction only; v41e-v-11 decision `PASS` unchanged.

## Correction

The Kilo report `v41e_v_11_findings.json` has sha256:

`2058547b46cbbd010a0aace824831dc1d8b44c7677df0d537de219317d16923a`

Its `evidence.zip_bundle` field contains the stale v41e-v-10 hash:

`sha256:205d22f39d128dd8666822a7d570bbd46f499b207d2ba48c2f36ad7f7d8651c1`

The v41e-v-11 bundle actually verified in its check `PV-02` is:

`sha256:c482b969f478da71129af93679948a89c9f3724f651aaa119dc3aa70ddc645a0` (26,916 bytes, 8 files).

## Effect

- `PV-02` and all v11 checks remain valid; only the metadata field is stale.
- Corrected statement: **v11 bundle = c482b969…; v10 bundle = 205d22f3…**.
- No change to the PASS decision.

## Linkage

This record is hash-linked to the v11 findings hash above. It does not alter the Kilo report file. Published with detached signature.
