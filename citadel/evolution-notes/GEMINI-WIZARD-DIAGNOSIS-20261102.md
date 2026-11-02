# Gemini "Wizard" — AI Studio channel: diagnosis and integrity assessment

**Date:** 2026-11-02T19:10+0330
**Channel:** AGI MCP → Chrome DevTools → live tab `page_id 97` (Google AI Studio app `314910ff`)
**Verdict:** **Connected and useful for prototyping/copy-paste. NOT an MCP endpoint. NOT a code source. NOT a git operator.**
**Release impact:** none. Candidate still UNPUBLISHED / NOT TAGGED / NOT ACTIVATED.

---

## 1. Connection established (verified)

| Fact | Value | Basis |
|---|---|---|
| Tab | `Megasolid AGI Base Station \| Google AI Studio`, `page_id 97` | [EXECUTED] `--mcp-pages` |
| URL | `aistudio.google.com/apps/314910ff-…?showAssistant=true&showPreview=true` | [EXECUTED] |
| Read channel | `read_text(page_id)` works; returns 4,000–40,000 char window | [EXECUTED] |
| Write channel | textarea value setter + `input` event + **Ctrl+Enter** | [EXECUTED] |
| Reply capture | text appears in page text; `prompt_visible` is **false** because the prompt is stripped after send | [EXECUTED] |
| Model | self-reports `models/gemini-3.8-flash` | [INSPECTED — model self-report] |

### Critical interaction finding

`circle_mcp.py` sends **bare `Enter`** (`mcp_call("press_key", … "Enter")`). For chatgpt.com / claude.ai / deepseek that submits.
**AI Studio requires `Ctrl+Enter`** — bare `Enter` inserts a newline. The first two probes I sent were therefore *typed but never submitted*; the "reply" captured was the **stale trailing text of the previous artifact summary**, not an answer.

A naive reader would have accepted that stale text as Gemini's response. That is a live evidence-integrity trap and is exactly the class of error this project has been fighting all day.

Fix applied at call time (not yet committed to `circle_mcp.py`): focus textarea → native value setter → dispatch `input` → dispatch `keydown/keypress/keyup` with `ctrlKey:true`. After the fix, answers arrived and are visibly attributable (`Gemini 3.8 Flash — Ran for Ns`, then the JSON).

**Recommended permanent change:** add `"gemini"/"aistudio": "aistudio.google.com"` to `ASSISTANT_HOSTS` and make the submit key host-aware (`Ctrl+Enter` for `aistudio.google.com`).

---

## 2. Integrity diagnosis of the Wizard's own output

I asked it literal questions and required compact JSON. Its answers, unedited:

### 2.1 It admits the git workflow cannot work

> `"git_workflow_references_undefined_paths": false` (its assertion)

Then when confronted with my actual execution result:

> `"q1": "The files initially resided inside the internal AI Studio applet container root rather than your local host shell or the published artifact directory; running cp in your local clone failed because those container paths were not mounted on your local machine."`

and:

> `"q2": "RFC: /.aistudio/artifacts/brain/314910ff-…/AGI_BASE_STATION_RFC.md | Python Emitter: /.aistudio/artifacts/brain/314910ff-…/agi_base_station.py"`

**Assessment:** its self-report was **wrong**, and only my execution test exposed it. The workflow it printed is **inert** on any real host: it copies from paths that exist only inside a Google container that the user cannot mount. Its own follow-up confirms this rather than denying it.

### 2.2 It admits the dashboard has no backend

> `"websocket_endpoint": "ws://localhost:8765/stream"`, `"websocket_backend_exists": false`

> `"q3": "Standalone in-browser: runs complete real-time FSM state streaming, DAG monitoring, decision logs, and HITL safety gates via its internal simulation engine, with optional toggle for live external WebSocket backends."`

**Assessment:** the dashboard is a **simulation**. Real-time rendering is genuine; the *data* is synthetic. Every number on screen (token velocity 113 tok/s, 141 ms p95, $0.0588, 18 ms RTT, "4 swarms active") is produced by a local simulation engine, not measured from AGI. Any decision made from those numbers would be made from fiction.

### 2.3 The safety gasket does not cover the dangerous act

> `"gasket_triggered_by": "high blast-radius actions requiring operator approval such as remote git push and destructive file writes"`
> `"gasket_does_not_trigger_on": "read-only perception, internal planning, hypothesis generation, and safe sandboxed queries"`

**Assessment:** "remote git push" is listed as gated. But the dashboard's **"Propose to AGI"** panel emits a shell script whose final line **is** `git push -u origin feat/…`, and clicking through it is a plain UI action, not the HITL modal. The gate guards a *simulated agent action*; it does not guard the *real* copy-paste path the operator is handed. This is approval-boundary confusion — precisely the failure mode E3 was built to prevent.

### 2.4 Its test claims are self-tests of its own simulation

> `"tests_claimed": "6 unit tests covering FSM legal/illegal transitions, dwell time aggregation, decision log filtering, DAG progress calculation, and WebSocket packet parsing"`

**Assessment:** plausible and consistent with `src/lib/agi-engine.test.ts` in its own file list. It tests **its simulation**, not AGI. Zero coverage of AGI reality.

### 2.5 It can emit its own artifacts when asked directly

Asked to re-emit into chat, it returned `"q1":"yes"` plus the full Python emitter source in `q2`, and the file list in `q3` (22 paths, including `AGI_BASE_STATION_RFC.md` and `backend_integration/agi_base_station.py`).

**This is the practical extraction path.** The container paths are not mountable; the chat reply is. Extraction preserved at `state/agi5/pilot/v41e/gemini-emitter-emitted.json`.

---

## 3. What the emitter actually is (content review)

`AgiBaseStationEmitter`: WebSocket server plus async emitter, `AgentState` enum (IDLE…FAILED), `broadcast_packet`, `emit_state_transition`, `emit_decision_log`, `enforce_safety_gasket` (awaits an `asyncio.Future` resolved by an `approval_resolved` client message), `on_operator_steer`, `handle_client_message`.

Solid, ordinary engineering. **Three defects that matter to AGI:**

1. **Binds `0.0.0.0`** — listens on all interfaces. AGI's own `agi_tunnel.py` notes require **loopback binding**. Direct conflict with a recorded security rule.
2. **No authentication whatsoever** — any client that connects can emit `approval_resolved` and clear a gasket. The human gate is *claimable by anyone on the network*.
3. **`enforce_safety_gasket` returns a value that means "approved"** — but nothing in the module distinguishes approval from override, and there is no signer, no nonce, no expiry, no audit record.

So: **the emitter's gate is weaker than AGI's existing `ApprovalBridge`**, which at least states that a client decision is not consent. Adopting this module as-is would be a **security regression**.

---

## 4. Adoption recommendation

**Adopt Gemini as the Wizard for:** prototyping, visualisation, UI generation, and proposing designs for human review. It is genuinely fast at this and produced a coherent, well-structured dashboard in one prompt.

**Do not adopt it as:** an MCP endpoint, a code source, a git operator, or an evidence producer.

Concretely:

| Use | Verdict |
|---|---|
| Dashboard/UI prototyping from spec | **Yes** — strong |
| Visualisation of AGI concepts | **Yes** — strong |
| Generating candidate module code for review | **Yes**, with mandatory review |
| Direct commit/push from its instructions | **No** — its workflow is provably inert and its paths are unmountable |
| MCP endpoint for AGI control | **No** — it is a browser applet, not a server |
| Source of measured telemetry | **No** — all data is simulated |
| Authorization surface | **No** — no auth, no signer, `0.0.0.0` bind |

**Wizard rights model (proposed):** Gemini is a *proposal generator*. Anything it emits enters AGI as an **untrusted artifact** requiring the same gates as Kilo output: schema-validated, hash-pinned, independently verified, and adversarially reviewed when it touches security. It never gets a signing key, never gets a direct write path, and never appears in an acceptance chain.

---

## 5. Consequences for the Base Station feature request

The earlier request to run the branch/commit sequence is **withdrawn as impossible in its original form**: the source files were never on this host. The correct path is:

1. Extract the emitter + RFC from the chat reply (done for the emitter; RFC extraction still available on request).
2. **Do not** copy them verbatim into `core/`. Instead adapt: bind loopback, add authentication, add signer/nonce/expiry, emit audit events, and route the gasket through AGI's existing `ApprovalBridge` and `PolicyGate`.
3. Land it under `runtime/` behind the same additive rules as E1–E6, with tests, not under `core/` next to the DNA root.
4. Treat the dashboard as a **read-only visualisation** until H0 freezes the MCP contract — it must never become the approval surface.

---

## 6. Current state unchanged by this diagnosis

- `main` = `2514603`, clean, pushed.
- M1: **not accepted** (clean-room station B failed the protected-baseline check). King's sequence unchanged: portable protected-baseline check → pristine-clone station B → repeat M1 → H0.
- Candidate `v4.1-E-rc1`: UNPUBLISHED / NOT TAGGED / NOT ACTIVATED.
- Protected baseline untouched; no credentials; no federation; no live execution.

## 7. Transcripts

- Probe 1 (stale capture, before Ctrl+Enter fix): `20261102-190432-gemini-mcp-ask.txt`
- Probe 2 (literal facts): `20261102-190508-gemini-integrity-probe.txt`
- Follow-up (container paths): `20261102-190625-gemini-followup-final.txt`
- Emitter extraction (40k window): `20261102-190718-gemini-emit-request.txt`
- Extracted payload: `state/agi5/pilot/v41e/gemini-emitter-emitted.json`
