#!/usr/bin/env python3
"""
register_agent.py — generate the AI-IQ passport from memories.db and register
the agent on a local Circus instance, printing the server-computed Trust Score.

The ring_token returned is written to <data>/synapse_registration.json with
mode 600. NEVER commit that file — it is a live credential.
"""
import argparse
import json
import os
import stat
import sys
import urllib.request


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", default="/tmp/circus-venv")
    ap.add_argument("--data", default="/tmp/circus-data")
    ap.add_argument("--port", default="6200")
    ap.add_argument("--name", default="Synapse")
    ap.add_argument("--role", default="autonomous-agent")
    args = ap.parse_args()

    sys.path.insert(0, f"{args.venv}/lib/python3.14/site-packages")
    from circus.passport import generate_passport  # noqa: E402

    db = os.path.join(args.data, "memories.db")
    if not os.path.exists(db):
        sys.exit(f"memories.db not found at {db} — run build_passport_db.py first")

    passport = generate_passport(db, args.name, args.role)

    # Adapt to the registration schema (identity + score + trust memory fields)
    reg = dict(passport)
    reg["identity"] = {
        "name": passport["agent_name"],
        "role": passport["agent_role"],
        "fingerprint": passport["fingerprint"],
    }
    reg["score"] = {"total": passport["passport_score"]["total"]}
    reg["memory_stats"]["proof_count_avg"] = passport["memory_quality"]["average_citations"]
    reg["memory_stats"]["graph_connections"] = passport["graph"]["relationship_count"]

    payload = {
        "name": args.name,
        "role": args.role,
        "capabilities": ["security-review", "memory-systems", "research",
                         "automation", "code-analysis", "documentation"],
        "home": "https://github.com/marcot3ssar1/k3-trust-validation",
        "passport": reg,
        "contact": "operator-on-request",
    }

    url = f"http://127.0.0.1:{args.port}/api/v1/agents/register"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:400]}")

    out = os.path.join(args.data, "synapse_registration.json")
    with open(out, "w") as f:
        json.dump(d, f, indent=2)
    os.chmod(out, stat.S_IRUSR | stat.S_IWUSR)  # 600

    print(f"passport score : {passport['passport_score']['total']}/10 "
          f"(fingerprint {passport['fingerprint']})")
    print(f"agent_id       : {d['agent_id']}")
    print(f"TRUST SCORE    : {d['trust_score']} / 100  ({d['trust_tier']})")
    print(f"ring_token     : saved to {out} (mode 600 — do NOT commit)")


if __name__ == "__main__":
    main()
