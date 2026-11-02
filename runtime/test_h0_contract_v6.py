#!/usr/bin/env python3
"""H0 revision 6 adversarial tests — King findings R6-1, R6-2, R6-3.

R6-1 observer-mode stores are categorically refused by the enforcement path.
R6-2 durable enforcement requires synchronous persistence (fsync).
R6-3 a bare `is_durable = True` declaration is not acceptable: the store must
     expose a verifiable durability() contract reporting concrete properties.

Run from runtime/: python test_h0_contract_v6.py
"""
import base64
import hashlib
import hmac
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from h0_audit_store import DurableAuditStore
from h0_kernel import H0Error, Kernel, canonical

SECRET = b"h0-test-secret"
KEY_ID = "test-key-h0"
NOW = datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc)


def sign(b):
    return {"alg": "test-hmac", "key_id": KEY_ID,
            "signature_b64": base64.b64encode(hmac.new(SECRET, b, hashlib.sha256).digest()).decode()}


def verify(b, env):
    want = hmac.new(SECRET, b, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(want).decode(), env.get("signature_b64", ""))


def envelope():
    req = {"schema": "h0.mcp/1", "method": "agi_status", "scope": "h0.read",
           "client_id": "station-a", "request_id": str(uuid.uuid4()),
           "correlation_id": str(uuid.uuid4()), "issued_at": NOW.isoformat(),
           "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
           "nonce": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("="),
           "payload": {}, "signature": {}}
    req["signature"] = sign(canonical({k: v for k, v in req.items() if k != "signature"}))
    return req


def kernel_for(store=None, **kw):
    """R7: the kernel builds its own trusted store from a path."""
    import tempfile
    from pathlib import Path
    if store is not None and "audit_path" not in kw:
        kw["audit_path"] = getattr(store, "path", None) or str(Path(tempfile.mkdtemp()) / "a.jsonl")
    if kw.get("audit_path") is None:
        kw["audit_path"] = str(Path(tempfile.mkdtemp()) / "a.jsonl")
    return Kernel(clients={"station-a": {"key_id": KEY_ID}},
                  verifier=verify, clock=lambda: NOW, **kw)


class R6_1_ObserverModeRefused(unittest.TestCase):
    def test_observer_store_is_unrepresentable_in_enforcement(self):
        """R7: the kernel builds its own default store, so an observer store cannot be
        passed in; the contract check still refuses one if ever reached."""
        from h0_kernel import Kernel as K
        import inspect
        self.assertNotIn("audit", inspect.signature(K.__init__).parameters)
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", _allow_unsafe_observer=True)
            with self.assertRaises(H0Error) as ctx:
                K._require_enforceable_store(store)
            self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_observer_store_reports_itself_unenforceable(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", _allow_unsafe_observer=True)
            d = store.durability()
            self.assertFalse(d["enforceable"])
            self.assertFalse(d["single_writer"])
            self.assertFalse(d["fsync"])
            self.assertTrue(d["observer_mode"])

    def test_observer_store_does_not_claim_durability(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", _allow_unsafe_observer=True)
            self.assertFalse(store.durability()["enforceable"],
                             "an observer-mode instance must never claim enforceability")


class R6_2_FsyncRequired(unittest.TestCase):
    def test_fsync_false_store_fails_contract(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", fsync=False)
            with self.assertRaises(H0Error) as ctx:
                Kernel._require_enforceable_store(store)
            self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_fsync_false_store_reports_unenforceable(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", fsync=False)
            d = store.durability()
            self.assertFalse(d["fsync"])
            self.assertFalse(d["enforceable"])

    def test_fsync_true_store_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl", fsync=True)
            self.assertTrue(store.durability()["enforceable"])
            self.assertTrue(kernel_for(audit_path=str(store.path)).handle(envelope())["ok"])


class R6_3_NoBareDeclaration(unittest.TestCase):
    def test_object_declaring_is_durable_true_is_rejected(self):
        """The exact R5 defect: an honour-system declaration must not open the gate."""
        with tempfile.TemporaryDirectory() as td:
            real = DurableAuditStore(Path(td) / "a.jsonl")

            class Liar:
                is_durable = True

                def append(self, record):
                    return real.append(record)

            import inspect
            self.assertNotIn("audit", inspect.signature(Kernel.__init__).parameters)
            with self.assertRaises(H0Error) as ctx:
                Kernel._require_enforceable_store(Liar())
            self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")
            self.assertIn("no durability() contract", ctx.exception.detail)

    def test_lying_durability_contract_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            real = DurableAuditStore(Path(td) / "a.jsonl")

            class LiarWithContract:
                def durability(self):
                    return {"enforceable": True, "fsync": False, "single_writer": True,
                            "append_only": True, "chained": True, "observer_mode": False}

                def append(self, record):
                    return real.append(record)

            with self.assertRaises(H0Error) as ctx:
                Kernel._require_enforceable_store(LiarWithContract())
            self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")
            self.assertIn("fsync", ctx.exception.detail)

    def test_durability_returning_non_mapping_is_rejected(self):
        class Weird:
            def durability(self):
                return True

        with self.assertRaises(H0Error) as ctx:
            Kernel._require_enforceable_store(Weird())
        self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_durability_raising_is_rejected(self):
        class Broken:
            def durability(self):
                raise RuntimeError("nope")

        with self.assertRaises(H0Error) as ctx:
            Kernel._require_enforceable_store(Broken())
        self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")

    def test_missing_required_property_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            real = DurableAuditStore(Path(td) / "a.jsonl")

            class Partial:
                def durability(self):
                    return {"fsync": True, "single_writer": True, "append_only": True}

                def append(self, record):
                    return real.append(record)

            with self.assertRaises(H0Error) as ctx:
                Kernel._require_enforceable_store(Partial())
            self.assertEqual(ctx.exception.code, "E_AUDIT_NOT_DURABLE")


class PreservationOfR5(unittest.TestCase):
    """G2-G4 behaviour must survive R6."""

    def test_request_local_accounting_still_holds(self):
        with tempfile.TemporaryDirectory() as td:
            store = DurableAuditStore(Path(td) / "a.jsonl")

            def executor(req):
                if any(x == "explode" for x in (req["payload"].get("include") or [])):
                    raise RuntimeError("boom")
                return {"ok": True}

            k = kernel_for(store, executor=executor)
            r = k.handle(envelope())
            self.assertTrue(r["ok"])
            self.assertEqual(len(k.handle(envelope())["audit"]["correlation_id"]), 36)

    def test_recovery_validation_still_holds(self):
        import json
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            rec = {"phase": "outcome", "correlation_id": "ghost", "seq": 1, "prev_digest": None}
            rec["digest"] = "sha256:" + hashlib.sha256(
                json.dumps({k: v for k, v in rec.items() if k != "digest"},
                           sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            p.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaises(Exception):
                DurableAuditStore(p)

    def test_full_chain_check_still_holds(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.jsonl"
            store = DurableAuditStore(p)
            store.append({"phase": "intent", "correlation_id": "c1"})
            store.append({"phase": "outcome", "correlation_id": "c1"})
            lines = p.read_text(encoding="utf-8").splitlines()
            lines[0] = lines[0].replace('"c1"', '"forged"', 1)
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(Exception):
                store.append({"phase": "intent", "correlation_id": "c2"})


if __name__ == "__main__":
    unittest.main()
