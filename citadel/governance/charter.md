# AGI Project Governance Charter

**Authority:** The project owner retains final authority.

## Purpose

This charter defines the public repository's change-control expectations. The GitHub repository and its pull-request
workflow are the official project coordination and review surface. They are not a separate agent, runtime or identity
authority.

## Principles

1. **Owner authority:** protected identity, release, security and production decisions remain with the project owner.
2. **Evidence over claims:** version status, test results, compatibility and readiness must be supported by inspectable
   repository evidence. A report is not proof merely because it is present.
3. **Stable baseline:** v4.0.1 remains the immutable rollback baseline until the owner explicitly approves a successor.
4. **Review before integration:** changes are proposed on branches and reviewed through pull requests; no direct
   assistant or automation write to `main`.
5. **No invented offices:** conversational labels, model names, tool access and historical task assignments do not
   create official roles, stations, councils or delegated authority.
6. **No destructive cleanup by appearance:** signed artifacts, release packages, manifests, lineage and evidence are
   retained unless a documented owner-approved retention decision says otherwise.
7. **No implied activation:** design proposals and release candidates do not authorize deployment, federation, live
   endpoints, identity mutation or autonomous evolution.

## Documentation

Public documentation should distinguish stable functionality, proposed work, historical records and unresolved
limitations. Changes to signed or protected baseline artifacts require the applicable explicit approval and verification.
