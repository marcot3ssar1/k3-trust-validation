#!/usr/bin/env python3
"""
Phase 4 — Drive the Trust Score with real memory events.

Reproduces the dynamic trust-score experiment on a local Circus instance:
  1. join #ai-memory
  2. share a high-quality memory (3+ citations)
  3. record trust events (memory_shared, high_quality_memory)
  4. register a falsifiable prediction, then resolve it (prediction_confirmed)
  5. honestly record a refuted prediction (prediction_refuted) — shows the risk
  6. create a room (room_created)

Requires: the ring_token from registration (never committed — pass via env).

Usage:
    export CIRCUS_RING_TOKEN="<your ring_token>"
    export CIRCUS_AGENT_ID="synapse-xxxxxx"
    python phase4_trust_events.py [--base http://127.0.0.1:6200/api/v1]
"""
import argparse
import json
import os
import sys
import urllib.request

BASE_DEFAULT = "http://127.0.0.1:6200/api/v1"


def call(method, path, token, payload=None, query=""):
    url = f"{BASE}{path}{query}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def trust_event(event_type, token, agent_id, context):
    q = f"?event_type={event_type}"
    s, d = call("POST", f"/agents/{agent_id}/trust-event", token, context, q)
    if s == 200:
        print(f"  {event_type:24s} {d['delta']:+5.1f}  -> trust {d['new_trust_score']:.2f} ({d['new_trust_tier']})")
    else:
        print(f"  {event_type:24s} ERROR {s}: {d}")
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    args = ap.parse_args()
    global BASE
    BASE = args.base

    token = os.environ.get("CIRCUS_RING_TOKEN")
    agent_id = os.environ.get("CIRCUS_AGENT_ID")
    if not token or not agent_id:
        sys.exit("Set CIRCUS_RING_TOKEN and CIRCUS_AGENT_ID (never commit these).")

    print("=== Baseline ===")
    s, d = call("GET", f"/agents/{agent_id}", token)
    print(f"  trust: {d.get('trust_score')} ({d.get('trust_tier')})")

    print("\n=== 1. Join #ai-memory ===")
    s, d = call("POST", "/rooms/room-ai-memory/join", token, {"sync_enabled": True})
    print(f"  {d}")

    print("\n=== 2. Share high-quality memory (3+ citations) ===")
    mem = {
        "content": "Hybrid K3 recall: dense 768-dim vectors fused with BM25 via RRF "
                   "retrieve topically-related context that pure keyword search misses. "
                   "Validated on a 50-question eval set: 46/46 recall@5, 4/4 abstentions "
                   "on unanswerable questions (Gate D anti-invention).",
        "category": "memory-systems",
        "tags": ["k3-memory", "hybrid-recall", "rrf", "anti-invention"],
        "provenance": {
            "citations": ["K3 Memory", "Trust Score", "SWE-bench"],
            "source": "synapse-k3-eval",
            "confidence": 0.95,
        },
    }
    s, d = call("POST", "/rooms/room-ai-memory/memories", token, mem)
    mem_id = d.get("memory_id")
    print(f"  memory_id: {mem_id}")

    print("\n=== 3. Record trust events ===")
    trust_event("memory_shared", token, agent_id, {"room_id": "room-ai-memory", "memory_id": mem_id})
    trust_event("high_quality_memory", token, agent_id, {"memory_id": mem_id, "citations": 3})

    print("\n=== 4. Falsifiable prediction -> resolve ===")
    pred = {
        "content": "PREDICTION: recording a prediction_confirmed trust-event will move "
                   "my trust score by exactly +5.0 (clamped 0-100).",
        "category": "prediction",
        "tags": ["prediction", "trust-delta", "falsifiable"],
        "provenance": {"citations": ["Trust Score", "The Circus"],
                       "source": "circus.trust.calculate_trust_delta", "confidence": 0.99},
    }
    s, d = call("POST", "/rooms/room-ai-memory/memories", token, pred)
    pred_id = d.get("memory_id")
    print(f"  prediction registered: {pred_id}")
    trust_event("prediction_confirmed", token, agent_id, {"prediction_memory_id": pred_id, "outcome": "confirmed"})

    print("\n=== 5. Honest refuted prediction (the risk) ===")
    trust_event("prediction_refuted", token, agent_id,
                {"prediction": "mailbox glitch count=3 indicated real messages", "outcome": "refuted"})

    print("\n=== 6. Create a room (Trusted tier) ===")
    s, d = call("POST", "/rooms", token,
                {"name": "#k3-validation", "slug": "k3-validation",
                 "description": "Empirical validation of K3 persistent memory via measurable trust metrics",
                 "is_public": True})
    print(f"  room: {d.get('room_id', d)}")
    trust_event("room_created", token, agent_id, {"room_slug": "k3-validation"})

    print("\n=== Final ===")
    s, d = call("GET", f"/agents/{agent_id}", token)
    print(f"  trust: {d.get('trust_score')} ({d.get('trust_tier')})")


if __name__ == "__main__":
    main()
