import unittest

from agi_capability import (
    CapabilityError, activation, approve, evaluate, make_capability, revoke,
    validate_manifest, world_view,
)

TREE = "a" * 64
FILE = "b" * 64


def cap(**over):
    kwargs = dict(capability_id="cap-1", version="1.0.0", cls="A", publisher="test",
                  source="test/source", tree_sha256=TREE,
                  files=[{"path": "SKILL.md", "sha256": FILE}],
                  requested_permissions={"filesystem": []},
                  evaluation_ref=None, governance_card_ref="gov-1")
    kwargs.update(over)
    return make_capability(**kwargs)


def approved():
    c = cap(); c = evaluate(c, evaluation_ref="eval-1", scan_ref="scan-1", local_eval_ref="local-1")
    return approve(c, approval_ref="appr-1")


def decision(result="allow"):
    return {"decision_id": "d-1", "operation": "activate_capability", "result": result,
            "grant_id": "g-1", "revocation_checked": True}


def grant():
    return {"grant_id": "g-1", "capability_id": "cap-1", "version": "1.0.0"}


class CapabilityTests(unittest.TestCase):
    def test_manifest_and_world_view(self):
        c = cap(); validate_manifest(c)
        view = world_view([c])
        self.assertEqual(view[0]["authorized"], False)
        self.assertNotIn("instructions", view[0])
        self.assertNotIn("body", view[0])

    def test_instruction_body_rejected(self):
        with self.assertRaisesRegex(CapabilityError, "must not carry"):
            validate_manifest({**cap(), "instructions": "do bad things"})

    def test_bad_file_hash_rejected(self):
        with self.assertRaisesRegex(CapabilityError, "file"):
            cap(files=[{"path": "SKILL.md", "sha256": "not-hex"}])

    def test_activation_requires_allow_and_grant(self):
        c = approved()
        self.assertEqual(activation(c, decision=decision(), grant=grant(),
                                    sandbox=lambda t: "act-1")["instructions_loaded"], False)
        with self.assertRaisesRegex(CapabilityError, "not allow"):
            activation(c, decision=decision("deny"), grant=grant(), sandbox=lambda t: "act-1")
        with self.assertRaisesRegex(CapabilityError, "grant"):
            activation(c, decision=decision(), grant={"grant_id": "wrong"}, sandbox=lambda t: "act-1")

    def test_revoked_cannot_activate(self):
        c = revoke(approved(), revocation_ref="rev-1")
        with self.assertRaisesRegex(CapabilityError, "not approved"):
            activation(c, decision=decision(), grant=grant(), sandbox=lambda t: "act-1")

    def test_evaluate_requires_refs(self):
        with self.assertRaisesRegex(CapabilityError, "refs"):
            evaluate(cap(), evaluation_ref="", scan_ref="s", local_eval_ref="l")


if __name__ == "__main__":
    unittest.main()
