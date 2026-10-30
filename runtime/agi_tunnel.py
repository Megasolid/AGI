#!/usr/bin/env python3
"""agi_tunnel - tunnel readiness check and plan for the beta MCP bridge (never opens a tunnel itself).

The beta bridge binds 127.0.0.1 only. To let a web season reach it, a tunnel must be authenticated and
policy-scoped; this helper only detects what is installed, prints a reviewed plan, and refuses to pretend
a tunnel exists when the binary is absent.

CLI:
    python runtime/agi_tunnel.py --check
    python runtime/agi_tunnel.py --plan --port 8766 [--hostname agi.example.com]
"""
import argparse
import json
import pathlib
import shutil

SCHEMA = "agi-tunnel/1"
SECURITY = [
    "bridge stays bound to 127.0.0.1; the tunnel terminates outside and forwards only to it",
    "MCP requires a bearer token with scopes; never expose the bridge without a token",
    "prefer an access policy (Cloudflare Access / Tailscale ACL) over a public quick tunnel",
    "approve_intent remains local-only; remote clients can queue intents but never approve",
    "rotate the bridge token after any tunnel exposure; log every remote call",
]


def which(name):
    return shutil.which(name)


def check():
    cloudflared = which("cloudflared")
    tailscale = which("tailscale")
    return {"ok": True, "schema": SCHEMA, "tools": {"cloudflared": cloudflared, "tailscale": tailscale},
            "any_available": bool(cloudflared or tailscale),
            "verdict": "ready" if (cloudflared or tailscale) else "blocked (no tunnel binary installed)",
            "security": SECURITY,
            "note": "this helper never starts a tunnel; it only reports readiness and plans"}


def plan(port=8766, hostname=None, token_file=None):
    c = check()
    cmds = []
    if c["tools"].get("cloudflared"):
        if hostname:
            cmds.append({"name": "cloudflared-named", "cmd": "cloudflared tunnel --url http://127.0.0.1:%d --hostname %s"
                                                             % (port, hostname),
                         "auth": "Cloudflare Access policy required; named tunnel + DNS"})
        cmds.append({"name": "cloudflared-quick", "cmd": "cloudflared tunnel --url http://127.0.0.1:%d" % port,
                     "auth": "quick tunnel is public - use only with a token AND an access policy"})
    if c["tools"].get("tailscale"):
        cmds.append({"name": "tailscale-funnel", "cmd": "tailscale funnel %d on" % port,
                     "auth": "Tailscale ACL; funnel exposes to tailnet/public depending on config"})
    return {"ok": bool(cmds), "schema": SCHEMA, "port": port, "readiness": c["verdict"],
            "commands": cmds, "token_file": token_file or "<sandbox>/state/bridge_token.json",
            "security": SECURITY,
            "note": "review the command and the access policy before running; AGI never opens ingress itself"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tunnel readiness + plan for the beta bridge")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--hostname", default=None)
    ap.add_argument("--token-file", default=None)
    a = ap.parse_args(argv)
    r = plan(a.port, a.hostname, a.token_file) if a.plan else check()
    print(json.dumps(r, indent=1))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
