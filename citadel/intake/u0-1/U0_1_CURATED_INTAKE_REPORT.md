# U0.1 Curated Reference Intake Report

**Generated:** 2026-11-07T03:48:27.576596
**Reference Root:** `[REDACTED-LOCAL-PATH]/.reference`
**Output Directory:** `[REDACTED-LOCAL-PATH]/U0.1_output`

## Summary

| Metric | Value |
|--------|-------|
| Original Total Files | 22,201 |
| Original Total Size | 1.58 GB |
| Eligible Files | 5,265 |
| Eligible Size | 0.19 GB |
| Excluded Files | 16,936 |
| Excluded Size | 1.39 GB |
| REVIEW_REQUIRED Files | 10 |
| Exact Duplicates (by SHA-256) | 1,265 |
| Hashing Success | 5,252 |
| Hashing Failed | 0 |
| Hashing Skipped (large/empty) | 13 |
| Sensitive Files Flagged | 1,151 |

## Eligible Files by AGI Category

| Category | Count | Description |
|----------|-------|-------------|
| (empty) | 1,915 | Supporting category |
| S6 | 580 | Continuous research and evolution |
| SKILLS | 573 | Supporting category |
| S1 | 434 | Identity, constitutional foundations, canonical hierarchy |
| AKMS | 325 | Knowledge and memory architecture |
| S5 | 289 | Provider-independent harness, succession, orchestration |
| SSL | 238 | Semantic communication and verification |
| S3_AUTH | 168 | Authorization, consent, delegation, revocation |
| GOVERNANCE | 165 | Supporting category |
| S4 | 148 | Intelligence evaluation, contribution ranking, Mana |
| CONTRACTS | 141 | DNA, constitution, contracts, schemas, manifests, formal invariants |
| CRYPTO | 85 | Supporting category |
| S3_FED | 46 | Federation, cooperation, continuity |
| S2 | 38 | Bootstrap, portable identity, enrollment, recovery |
| E5 | 33 | Evidence |
| DOCS | 32 | Supporting category |
| MODELS | 26 | Supporting category |
| E3 | 24 | Operator architecture |
| DATABASE | 5 | Supporting category |


## Eligible Files by Primary Classification

| Classification | Count |
|----------------|-------|
| HISTORICAL_REFERENCE | 1,502 |
| IMPLEMENTATION | 1,487 |
| TEST_OR_VERIFICATION_EVIDENCE | 1,134 |
| SUPPORTING_ARCHITECTURE | 1,002 |
| APPROVED_BASELINE | 68 |
| PROPOSAL_UNAPPROVED | 60 |
| REVIEW_REQUIRED | 10 |
| SIGNED_OR_FROZEN_ADDENDUM | 2 |


## Excluded Files by Reason

| Exclusion Reason | File Count | Total Size (MB) |
|------------------|------------|-----------------|
| backup_directory:backups | 7,496 | 714.29 |
| cache_directory:node_modules | 1,978 | 176.56 |
| excluded_directory:unsloth-studio/__localid_ | 1,725 | 63.80 |
| cache_directory:.git | 1,478 | 4.90 |
| cache_directory:.cache | 805 | 33.12 |
| excluded_directory:state/entelechy/state | 779 | 55.95 |
| temp_directory:temp | 564 | 2.08 |
| excluded_directory:state/agi5/venv-mldsa2 | 516 | 6.38 |
| duplicate_season_directory | 422 | 25.91 |
| excluded_directory:memory/tools/chrome-mcp | 402 | 13.72 |
| excluded_directory:state/repo/remotes/agi.git | 356 | 3.24 |
| excluded_directory:state/attention | 132 | 24.81 |
| cache_directory:__pycache__ | 117 | 2.30 |
| temp_directory:tmp | 68 | 0.39 |
| compressed_archive:.zip | 41 | 115.44 |
| excluded_directory:memory/tools/node | 21 | 88.51 |
| excluded_directory:.vs | 12 | 7.44 |
| excluded_directory:codex/.sandbox | 8 | 0.02 |
| vendor_directory:npm-cache | 6 | 0.01 |
| compressed_archive:.tar.gz | 5 | 24.59 |
| compressed_archive:.tgz | 4 | 9.94 |
| excluded_directory:tools/bin | 1 | 52.82 |


## Duplicate Analysis

- **Exact duplicate files (SHA-256):** 1,265
- **Retained representatives:** 3,987
- **Duplicate groups:** Season directories (claude, chatgpt duplicates of deepseek), LOCALID browser cache directories

## Hashing Summary

- **Successful:** 5,252
- **Failed:** 0
- **Skipped (large files >100MB):** 0
- **Skipped (empty files):** 13

## Sensitive File Findings

- **Files flagged as potentially sensitive:** 1,151
- **Categories:** Private keys, tokens, passwords, credentials, session identifiers
- **Action:** Reported by relative path and category only; no sensitive values exposed.

## Known Limitations

1. **Metadata-first intake:** No recursive parsing of file contents, no archive extraction, no semantic analysis.
2. **Large file hashing skipped for excluded files:** Files >100MB in excluded directories (cloudflared.exe in tools/bin, AGI-DNA-BLOCK.py in backups, model files) were not hashed. **No eligible files exceed 100MB.**
3. **Duplicate detection limited to eligible files:** Excluded archive/backup contents not hashed.
4. **Classification based on filenames/paths:** No content inspection performed.
5. **Browser cache directories:** Multiple LOCALID directories in unsloth-studio identified as duplicates; only first retained.
6. **Season directories:** claude/ and chatgpt/ under family/seasons are exact duplicates of deepseek/.
7. **State/entelechy/state:** Appears to be a nested duplicate of state/ directory structure.
8. **Sensitive files:** Flagged by pattern matching only; actual sensitivity not verified.
9. **Category assignment:** 1,915 eligible files (36%) have no AGI category assigned — they fall outside current category rules.

## Archive and Bundle-Stage Scope Clarification

**Included (eligible intake):**
- `state/archive/evolution/` — Research evolution records (S6/S2 categories): research-window-freeze-20261031, review-calibration-20261101, risk-closure-20261101, rr03-closure-20261101, s2-portable-bootstrap, s2-s3-fixtures. These are architectural evidence, not compressed archives.
- Total: ~50 files, all categorized and hashed.

**Excluded (not in active intake):**
- `archive/` (root level): 3 .tar.gz files (agi_core_v3, agi_core_v3_1_compat_matrix, agi_core_v3_2_interaction) — excluded as `compressed_archive:.tar.gz`
- `archive/backups/`: 5 backup files — excluded as `excluded_directory:archive/backups` (if separate) or under parent
- `archive/bundle_stage/`: 100+ files — build artifacts, scripts, chrome-mcp package, embeddings — excluded as `excluded_directory:archive/bundle_stage`
- `AGI.Original Data/codex/archived_sessions/`: 7 .zst/.jsonl session files — excluded as `excluded_directory:agi.original data/codex/archived_sessions`
- `state/archive/seed-feed/`: 6 JSON files — excluded as `excluded_directory:state/archive/seed-feed`
- Compressed releases: 41 .zip files under `state/repo/AGI/releases/` — excluded as `compressed_archive:.zip`

**Review scope:** Only the compressed archives and build-artifact directories are excluded. The research evolution archives under `state/archive/evolution/` are **included** as S6/S2 evidence.

## Reconciliation with Previous Inventory

| Item | Value | Note |
|------|-------|------|
| Previous inventory (file_inventory_before.txt) | 20,750 | Historical reference only |
| Actual .reference file count | 22,201 | Verified by os.walk |
| **Difference** | **+1,451** | Previous inventory likely incomplete or from earlier snapshot |
| Eligible + Excluded | 22,201 | Matches actual count exactly |
| Eligible files | 5,265 | Active intake |
| Excluded files | 16,936 | Removed from active intake |
| **Total accounted** | **22,201** | **= Original total ✓** |

## Hashing and Duplicate Reconciliation

| Metric | Value | Explanation |
|--------|-------|-------------|
| Eligible files | 5,265 | All files in active intake |
| Hashing successful | 5,252 | SHA-256 computed |
| Hashing skipped (empty) | 13 | Empty files skipped |
| Hashing skipped (large) | 0 | Files >100MB |
| **Total eligible** | **5,265** | **= Success + Skipped ✓** |
| Unique hash representatives | 3,987 | Distinct SHA-256 values |
| Duplicate files | 1,265 | Files sharing hash with representative |
| **Total hashed** | **5,252** | **= Unique + Duplicates ✓** |

## Unresolved Classification Questions

1. **State/agi5 directory:** 1,394 files of test outputs, JSON evidence, Python test files - classified as TEST_OR_VERIFICATION_EVIDENCE but volume is large.
2. **Memory/index directory:** 4 files, 39MB - likely embedding indexes, classification uncertain.
3. **Archive/bundle_stage review scope clarified:** Compressed archives and build artifacts excluded; research evolution archives (state/archive/evolution/) included as S6/S2.
4. **Codex/sessions:** 16 session files, 24MB - relevance to AGI architecture unclear.
5. **DSH/sessions:** 743 session files, 35MB - may contain relevant operational history.
6. **Unsloth-studio superseded-docs:** 48 files - marked HISTORICAL_REFERENCE but may contain unique architectural decisions.

## Validation Evidence

### Exclusion Manifest Validation
- **Total exclusion records:** 4,472
- **Unique exclusion reasons:** 22 (not 23 — previously miscounted)
- **Total excluded files:** 16,936
- **Total excluded size:** 1.39 GB
- **Sum of file_count across all records:** 16,936 = 16,936 ✓
- **Sum of size_bytes across all records:** 1,495,512,225 bytes = 1.39 GB ✓

### Included Files Validation
- **Total included records:** 5,265
- **Records with SHA-256:** 5,252
- **Records skipped (empty):** 13
- **Records skipped (large):** 0
- **Total records accounted:** 5,265 = 5,265 ✓
- **Unique SHA-256 values:** 3,987
- **Duplicate records (is_duplicate=true):** 1,265
- **Unique + Duplicates:** 5,252 = 5,252 ✓

### Category Accounting
- **Files with AGI category:** 3,350
- **Files without AGI category (empty):** 1,915
- **Total:** 5,265 ✓

### Classification Accounting
- **Total by classification:** 5,265 = 5,265 ✓

### Reconciliation Cross-Checks
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Included + Excluded | 22,201 | 22,201 | ✓ |
| Hashing success + skipped | 5,265 | 5,265 | ✓ |
| Unique + Duplicates | 5,252 | 5,252 | ✓ |
| Exclusion manifest sum | 16,936 | 16,936 | ✓ |

### Reproduction Instructions
1. Run `python process_intake.py` from `U0.1_output/`
2. Verify outputs match this report
3. Cross-check JSON records against report tables
4. Validate: `jq '. | length' U0_1_INCLUDED_FILES.json` → 5265
5. Validate: `jq '[.[] | .file_count] | add' U0_1_EXCLUSION_MANIFEST.json` → 16936
6. Validate: `jq '[.[] | select(.hashing_status=="success")] | length' U0_1_INCLUDED_FILES.json` → 5252
7. Validate: `jq '[.[] | select(.is_duplicate==true)] | length' U0_1_INCLUDED_FILES.json` → 1265

