# Rights-Holder and Provenance Inventory

**Purpose:** record who asserts authority to license the AGI project code and documentation, map license boundaries,
identify third-party exceptions, and define how mixed artifacts and artifact notices are handled.

**Not legal advice.** This is a project provenance record.

## 1. Rights-holder statement
- **Project owner / rights holder:** D (github.com/Megasolid), publishing as the AGI project.
- **Contributions:** project code and documentation were created by D with AI collaborators/agents under D's direction.
  To the extent permitted by law, D asserts authority to license those project materials under the licenses below.
  No representation is made that every AI-assisted portion is copyrightable in every jurisdiction.
- **Copyright notice:** `Copyright (c) 2026 D / AGI project contributors.`
- **Exceptions:** third-party material and private historical archive material are excluded from this assertion and are
  addressed separately below.

## 2. License mapping by artifact class

| Artifact class | Examples | License |
|---|---|---|
| Executable source | `runtime/*.py`, `tools/*.py`, `tests/*.py`, `*.sh`, `*.ps1`, `*.yml` | AGPL-3.0 (`LICENSE`) |
| Functional schemas/contracts | `core/dna.v4.json`, `contracts/*.schema.json`, executable manifests/configs | AGPL-3.0 |
| Documentation/prose | `README.md`, `USER_MANUAL.md`, `LINEAGE.md`, `CITADEL.md`, `citadel/**/*.md`, `docs/**` | CC BY-SA 4.0 (`LICENSE-docs`) |
| Documentary metadata | inventory/audit/decision-ledger records, pure description JSON | CC BY-SA 4.0 unless it is executable/functional |
| Signatures | `*.sig` | metadata; follows the signed artifact; no separate license grant |
| Release bundles | `releases/**/*.zip` | project code AGPL-3.0; project docs CC BY-SA 4.0; bundled third-party components keep their own terms |
| Diagrams/images | currently none tracked | if added, CC BY-SA 4.0 by default unless a specific notice says otherwise |
| Datasets | currently no public licensed datasets tracked | if added, require an explicit dataset license/notice; private archive excluded |
| Private historical archive | `AGI.Original Data/` | **PRIVATE / all rights reserved**; not published or relicensed; curated excerpts need explicit Owner consent, provenance and privacy review |

## 3. Mixed artifacts
- A file containing both prose and executable code is licensed **per part**: prose under CC BY-SA 4.0; code under
  AGPL-3.0.
- If code and prose cannot reasonably be separated, the code portions are AGPL-3.0 and the prose is CC BY-SA 4.0;
  the artifact notice must state the split.
- A documentation file that merely illustrates code (small examples) remains documentation for the prose and examples
  under CC BY-SA 4.0, while copying the code into a program triggers AGPL-3.0.
- Release manifests and `.sig` files do not change the license of the content they describe.

## 4. Artifact notices
- Release/artifact notices **supplement** the repository licenses and may not override or reduce them.
- A specific notice may clarify a specific artifact only when it is explicit, consistent with the repository grant, and
  does not purport to relicense third-party material.
- Artifact notices may supplement, but never override or reduce, the repository license grants. Third-party terms
  always prevail over any project claim; apparent conflicts must be recorded and reviewed, not resolved by treating the
  notice as a substitute license.
- No artifact notice in the reviewed tree grants broader rights than the repository licenses.

## 5. Third-party inventory and exceptions
- **Vendored third-party code/assets:** none identified in the tracked tree at the reviewed commit.
- **External dependencies** (for example optional Python packages such as `cryptography`, or the host SQLite library)
  are installed by the user/environment and remain under their own licenses; they are not relicensed by this project.
- **Referenced works:** public-domain writing references (for example *The Elements of Style*) are cited, not copied
  into the repository; their public-domain status is not a license for unrelated third-party material.
- **Release bundles:** reviewed file lists show project code/docs and signatures; no third-party license/notice file was
  found inside the tracked release zips. If a future bundle includes a third-party component, its notice and license
  must be added before release.
- **No third-party images, datasets or branded assets** were identified in the tracked tree at the reviewed commit.

## 6. Provenance and review
- Git history, signed release manifests and the decision ledger are the provenance record.
- The private historical archive is not part of the licensed publication and must not be published without explicit
  Owner consent and privacy/redaction review.
- This inventory was prepared for the KING's licensing-amendment review and must be updated if new artifact classes,
  third-party material or mixed-artifact rules are added.

**Reviewed:** 2026-10-31. **License decision:** Owner D chose AGPL-3.0 for code and CC BY-SA 4.0 for documentation.
