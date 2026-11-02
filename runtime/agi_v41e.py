#!/usr/bin/env python3
"""P7 integrated release-candidate smoke.

Exercises E1-E6 together using local mocks and temp files. This is a deterministic
integration check, not production readiness, an authority grant, or execution.
No network, credentials, live endpoints or frozen-baseline changes.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import tempfile
from pathlib import Path

from agi_capability import activation, approve, evaluate, make_capability, world_view
from agi_context import make_context_manifest
from agi_context_adapter import resolve_authorized
from agi_evidence import (
    EffectLedger, RecoveryController, gap_check, make_packet, reconcile,
)
from agi_handoff import completion_receipt, make_handoff, reconstruct_task
from agi_handoff_signing import sign_handoff, sign_receipt, verify_signed_handoff, verify_signed_receipt
from agi_operator import CancellationController, LeaseStore, PolicyGate, ServiceRegistry
from agi_operator_journal import OperatorJournal
from agi_sem import SemSession, constraint_digest, make_message, verify_semantics

TS = "2026-11-02T00:00:00+00:00"
EXP = "2026-11-03T00:00:00+00:00"
SECRET = b"p7-integration-mock-only"


def _sign(payload):
    sig = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return {"schema": "agi-sig/1", "alg": "test-hmac", "key_id": "test-key",
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "signature_b64": base64.b64encode(sig).decode("ascii")}


def _verify(payload, env):
    want = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode("ascii"), env.get("signature_b64", ""))


def _sem_message(mtype, seq, *, sender="mind-a", receiver="mind-b", body=None, constraints=None):
    return make_message(message_type=mtype, session_id="s1", message_id=f"m-{mtype}-{seq}",
                        sequence=seq, from_ref=sender, to_ref=receiver, body=body or {},
                        constraints=constraints or [], ts=TS, expires_at=EXP)


def run_smoke(root) -> dict:
    root = Path(root)
    steps = {}
    body = b"bounded context data"
    sha = hashlib.sha256(body).hexdigest()
    manifest = make_context_manifest(
        branch_id="br", provenance={"source": "p7-smoke"},
        refs=[{"context_id": "ctx-1", "branch_id": "br", "store": "memory/knowledge",
               "version": 1, "sha256": sha, "scope_digest": "a" * 64,
               "classification": "branch_private", "expires_at": EXP,
               "revocation_head_ref": "rh-1"}],
    )
    decision = {"decision_id": "d-1", "operation": "read_memory", "actor": "operator",
                "subject": "ctx-1", "grant_id": "g-1", "result": "allow",
                "reason_code": "ok", "ts": TS, "revocation_checked": True, "staleness_s": 0}
    resolved = resolve_authorized(manifest, manifest["refs"][0], allowed_branch="br",
                                  decide=lambda req: decision, gateway=lambda r: body,
                                  revocation_check=lambda h: h == "rh-1")
    steps["E1_context"] = resolved == body

    handoff = make_handoff(task_id="task-p7", title="integration", objective="bounded smoke",
                           owner="dsh", branch_id="br", context_manifest=manifest,
                           acceptance_criteria=["a"], evidence_requirements=["sha256"],
                           non_goals=["no network"], permissions={"read": True})
    signed = sign_handoff(handoff, _sign)
    verify_signed_handoff(signed, _verify)
    rebuilt = reconstruct_task(signed, lambda r: body)
    receipt = completion_receipt(signed, outcome="success", evidence_refs=["sha256:" + sha],
                                 constraints_met=["a"], residual_risks=[])
    verify_signed_receipt(sign_receipt(receipt, signed, _sign), signed, _verify)
    steps["E4_handoff"] = rebuilt["context"]["ctx-1"] == body and receipt["outcome"] == "success"

    constraints = [{"id": "C1", "kind": "MUST_NOT", "text": "no network",
                    "machine_check": "no_network", "source": "task", "enforcement": "runtime"}]
    constraints[0]["digest"] = constraint_digest(constraints[0])
    s = SemSession("s1")
    s.receive(_sem_message("HELLO", 1, body={"min_version": "0.2", "max_version": "0.2"}), now=TS)
    s.receive(_sem_message("HELLO_ACK", 1, sender="mind-b", receiver="mind-a", body={"version": "0.2"}), now=TS)
    s.receive(_sem_message("CAPABILITIES", 2, body={"classes": ["reasoning"]}), now=TS)
    s.receive(_sem_message("INTENT", 3, body={"goal": "read and summarize"}, constraints=constraints), now=TS)
    receipt_body = {"own_words": "I will only read and summarize", "constraint_check": [{"id": "C1", "preserved": True}],
                    "assumptions": [], "questions": [], "context_used": [], "probe_answer": "read-only", "confidence": 0.9}
    s.receive(_sem_message("SEMANTIC_RECEIPT", 2, sender="mind-b", body=receipt_body), now=TS)
    check = verify_semantics(receipt_body, intent_goal="read and summarize", constraints=constraints,
                             checker=lambda n, p: True, verifier_ref="mind-v",
                             sender_ref="mind-a", receiver_ref="mind-b",
                             semantic_verifier=lambda r, g: "PASS")
    s.receive(_sem_message("COMMIT", 4, body={}), now=TS)
    steps["E2_sem"] = check["result"] == "PASS" and s.state == "COMMITTED"

    journal = OperatorJournal(root / "operator-journal.jsonl")
    journal.append("ev-1", "run", {"task": "p7"})
    lease = LeaseStore(); lease.acquire("br", "operator", epoch=1, now=TS)
    lease.check_write("br", 1, now=TS)
    reg = ServiceRegistry(); reg.register("provider", start=lambda: None, stop=lambda: None); reg.start("provider")
    gate = PolicyGate(); gate.add_guard(lambda req: True)
    cancel = CancellationController(); cancel.request(); cancel.accept(); cancel.stopping()
    cancel.add_effect("e1"); cancel.mark_stopped("e1"); cancel.quiesce(); cancel.record()
    steps["E3_operator"] = (journal.last_seq == 1 and reg.state("provider") == "active"
                            and gate.decide({})["result"] == "allow"
                            and cancel.state == "recorded")

    cap = make_capability(capability_id="cap-p7", version="1.0.0", cls="A", publisher="test",
                          source="test", tree_sha256="b" * 64,
                          files=[{"path": "SKILL.md", "sha256": "c" * 64}],
                          requested_permissions={"filesystem": []}, governance_card_ref="gov-1")
    cap = approve(evaluate(cap, evaluation_ref="eval", scan_ref="scan", local_eval_ref="local"),
                  approval_ref="approval")
    act_decision = {"decision_id": "ad-1", "operation": "activate_capability", "result": "allow",
                    "grant_id": "ag-1", "revocation_checked": True}
    token = activation(cap, decision=act_decision,
                       grant={"grant_id": "ag-1", "capability_id": "cap-p7", "version": "1.0.0"},
                       sandbox=lambda t: "act-1")
    steps["E5_capability"] = token["instructions_loaded"] is False and world_view([cap])[0]["authorized"] is False

    packet = make_packet(run_id="run-p7", claim="smoke", evidence_refs=["sha256:" + sha],
                         environment={"host": "test"}, e_level="E1",
                         artifact_hashes={"ctx": sha})
    gap = gap_check(packet, ["sha256:" + sha])
    ledger = EffectLedger(root / "effects.jsonl")
    ledger.append("e1", "write", "emitted", "r1")
    ledger.append("e2", "network", "emitted", "r2")
    rec = reconcile([{"effect_id": "e1"}], ledger.effects())
    recovery = RecoveryController(); recovery.isolate(); recovery.replay()
    recovery.verify(state_digest_ok=True, effects_reconciled=False, lease_valid=True)
    steps["E6_evidence"] = gap["ok"] and rec["ok"] is False and recovery.state == "incident"

    return {"ok": all(steps.values()), "steps": steps, "schema": "agi/v41e/smoke/1",
            "note": "in-process integration smoke with mocks; not production readiness"}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        import json
        print(json.dumps(run_smoke(td), indent=1))
