# AGI Assistant Review Policy

## Default access mode

The default mode is targeted, read-only inspection. The assistant should read the task-relevant files, not recursively count or hash the entire repository.

## Source authority

Use the repository's own source hierarchy:

1. Signed DNA contract and its verification material for stable identity invariants.
2. Owner-approved governance and policy documents for authority and protected changes.
3. Canonical specifications and machine-readable contracts for subsystem behavior.
4. Implementation and tests for what is actually implemented.
5. Reports, handoffs, research notes and summaries as evidence with their own dates and scope.

A summary is not a substitute for the source it summarizes. A proposed architecture is not an implemented feature. A passing test is evidence only for the behavior it actually exercises.

## Change classes

- **Class A — review metadata and navigation:** skill instructions, workspace metadata, source maps and non-normative indexes. May be prepared in a task-authorized branch/PR.
- **Class B — ordinary documentation or tests:** requires task scope and compatibility review.
- **Class C — implementation, contracts, runtime behavior:** requires explicit task scope, targeted tests and required owner approval.
- **Class D — protected identity, signatures, releases, authorization, federation, production, live endpoints or destructive migration:** requires explicit owner authorization for the exact operation. Never infer authorization from a general request to review or improve AGI.

## File movement and cleanup

No file is moved or deleted based solely on age, naming, duplication suspicion, generated appearance, or lack of recent use.

Before a move:
1. Identify the file's role and references.
2. Determine whether it is canonical, historical, generated, release-sensitive, private, or disposable.
3. Check references from code, tests, scripts, manifests and documentation.
4. Define destination outside the active source root when appropriate.
5. Record source path, destination path, content hash or Git blob identity, reason, and rollback path.
6. Preserve signed and historical evidence unless the owner explicitly approves a retention change.

## Inventory and cost control

- Normal session: inspect changed paths and required dependencies.
- Checkpoint: update the change ledger and verify affected files.
- Migration checkpoint: perform a scoped reconciliation of the paths being migrated.
- Release/integrity checkpoint: perform the required complete verification.
- No daily recursive file count by default.

Git history and tree identity are used to establish change context. A Git tree SHA identifies a tree snapshot; it is not a substitute for per-file semantic review or a claim that all files have been individually validated.

## External workspace target

The eventual local workspace should have one clean active AGI root and a separate sibling area for non-active material, for example:

```text
AGI-WORKSPACE/
  AGI/                 # active canonical source
  AGI-EXTERNAL/
    archive/
    research/
    historical/
    migration/
    audit-evidence/
    generated/
    experiments/
    snapshots/
    staging/
```

This is a target layout proposal, not a statement that these directories currently exist or that the public repository must mirror the local workspace exactly.

## Non-goals

This policy does not authorize:
- Changing the stable V4 baseline or signed DNA.
- Declaring V5 implemented or release-ready.
- Activating SSL, federation, live endpoints or runtime integration.
- Changing identity, authority, authorization or governance.
- Deleting or rewriting historical evidence.
- Merging a PR, tagging a release or deploying a runtime.
