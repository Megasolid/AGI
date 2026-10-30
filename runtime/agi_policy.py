#!/usr/bin/env python3
"""agi_policy - explicit beta policy gates for Entelechy (beta.9).

Remote passport issuance is OFF by default. A local operator must enable it explicitly in
`<sandbox>/state/passport_policy.json` before the MCP `passport_issue` tool will issue a passport. Every policy
change is returned with its previous value so it can be logged.

CLI:
    python runtime/agi_policy.py --root <sandbox> --show
    python runtime/agi_policy.py --root <sandbox> --set remote_passport_issue_enabled=true
"""
import argparse
import json
import pathlib
import sys

SCHEMA = "agi-policy/1"
DEFAULT = {"remote_passport_issue_enabled": False}


def _path(root):
    return pathlib.Path(root).resolve() / "state" / "passport_policy.json"


def load(root):
    p = _path(root)
    try:
        data = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else dict(DEFAULT)
    except Exception:
        data = dict(DEFAULT)
    merged = dict(DEFAULT)
    merged.update(data or {})
    return merged


def allowed(root):
    return bool(load(root).get("remote_passport_issue_enabled"))


def set_value(root, key, value):
    cur = load(root)
    if key not in DEFAULT:
        return {"ok": False, "error": "unknown policy key %r" % key}
    old = cur.get(key)
    cur[key] = value
    p = _path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cur, indent=1), encoding="utf-8")
    return {"ok": True, "schema": SCHEMA, "policy": cur, "changed": {key: {"old": old, "new": value}},
            "note": "remote passport issuance is a privileged local decision"}


def _parse(v):
    if isinstance(v, str):
        if v.lower() in ("1", "true", "yes", "on"):
            return True
        if v.lower() in ("0", "false", "no", "off"):
            return False
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description="Beta policy gates (remote passport issuance off by default)")
    ap.add_argument("--root", required=True)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--set", metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    if a.set:
        key, _, val = a.set.partition("=")
        r = set_value(a.root, key.strip(), _parse(val.strip()))
    else:
        r = {"ok": True, "schema": SCHEMA, "policy": load(a.root),
             "remote_passport_issue_enabled": allowed(a.root)}
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
