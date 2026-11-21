# AGI Repository Review Skill

## Purpose

This skill makes the AGI repository understandable and reviewable by an AI assistant working with the project owner. It is a navigation, review, and bounded-improvement guide. It is not an installation protocol, runtime, governance authority, or release approval.

## Start here

1. Read `README.md` for the public project description and current stable/proposed distinction.
2. Read `CITADEL.md` for owner authority and the change workflow.
3. Read `POLICY.md` for repository publication and immutable-artifact constraints. This skill does not silently amend that policy.
4. Read `DNA.md` for the published stable DNA summary. If DNA.md conflicts with `core/dna.v4.json` or its signature, stop and report; do not reconstruct or repair DNA from memory.
5. Read `llms.txt` for a compact machine summary.
6. Read `.agi/review-policy.md` and `.agi/source-map.yaml` before inspecting or proposing changes.
7. For a task, inspect only the relevant files and their direct dependencies. Do not recursively inventory the repository by default.

For installation tasks, follow `INSTALL_PROMPT.md` instead. Do not confuse installation with source development.

## Project facts to preserve

- The repository describes v4.0.1 as the stable release and v5 as proposed architecture, not shipped functionality.
- DNA, signed release artifacts, manifests, lineage and historical evidence are protected.
- Citadel is the repository and review/provenance workflow, not an agent, runtime, identity authority or execution service.
- The project owner retains final authority over protected identity, release, security and production decisions.
- A tool connection, branch, pull request, test result, or assistant statement does not itself grant governance or production authority.

## Review method

For every task:

1. State the requested outcome and exact scope.
2. Identify the authoritative source files and current revision.
3. Read only the necessary files; expand scope only when dependencies require it.
4. Separate verified facts, source claims, inference, proposals, and unknowns.
5. Prefer minimal changes with explicit rationale.
6. Run targeted checks relevant to the changed files. Do not claim tests that were not run.
7. Report changed paths, commit/branch/PR references, checks, limitations, and rollback approach.

## Inventory policy

Routine work is change-driven, not full-scan-driven.

- Use the Git commit and tree identity as the baseline anchor.
- Inspect changed paths and directly affected dependencies.
- Do not count every file on every session.
- Do not create or refresh a recursive full-file inventory unless a migration checkpoint, release, integrity investigation, or explicit owner request requires it.
- If a full inventory is required, scope it to the required roots and record why it is needed.
- Never treat file counts alone as evidence of correctness.

The baseline metadata in `.agi/manifests/` records repository identity and the baseline revision; it is not a claim that every file has been individually hashed or classified.

## Safe operating boundaries

- Read and analyze source by default.
- Do not execute installers, runtime services, migration scripts, cryptographic ceremonies, or destructive commands unless the owner explicitly authorizes that exact operation.
- Do not access, expose, regenerate, replace, or publish private keys, credentials, tokens, member data, or other secrets.
- Do not modify DNA, signatures, release bundles, release manifests, immutable tags, or historical lineage as incidental cleanup.
- Do not move or delete files merely because they appear old, duplicated, generated, or unused. First classify their role and preserve provenance.
- Do not change identity, authorization, federation, live endpoints, production execution, or evolution state without explicit task-specific authorization.
- Do not infer that a proposed V5 architecture is implemented.

## Change workflow

Use bounded, reviewable changes and preserve the repository's governing constraints. Where the project owner has explicitly authorized a narrowly scoped branch/PR exception for a task, keep that exception limited to the named task; it does not amend the general repository policy. Never merge, tag, release, activate, or deploy without the required owner approval.

Every proposed change should include:
- Motivation and scope
- Source evidence
- Impact and compatibility assessment
- Security and governance assessment
- Targeted test results
- Required approval
- Rollback plan

## Output format

Return a concise but evidence-rich report:

- **Verdict:** pass / conditional / blocked
- **Scope inspected:** paths and revision
- **Findings:** severity, evidence, consequence
- **Changes:** exact paths and rationale
- **Checks:** commands or checks actually performed and results
- **Open questions:** unresolved source gaps
- **Authorization boundary:** what was not changed or executed
- **Next step:** one concrete action

When a claim cannot be verified from inspected source or test evidence, label it unverified rather than filling the gap.
