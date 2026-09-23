# Methodology

How the K3 → Trust Score experiment was run, and why it is (and isn't) evidence.

## Research question

Can the claimed properties of a persistent agent memory (accuracy, consistency,
quality) be turned into a number computed by **independent, third-party code** —
and does that number respond correctly to real memory events over time?

## Design

Two-phase design on a self-hosted [Circus](https://github.com/kobie3717/circus)
instance (`circus-agent` 1.1.0):

1. **Static measurement (Phases 1–3).** Export the agent's K3 working memory to
   an AI-IQ-compatible SQLite database, generate a passport, register, and read
   the server-computed Trust Score. Compare against an independent local
   calculation using the same `circus.trust` module.

2. **Dynamic measurement (Phase 4).** Drive the score with real events:
   share memories, register a falsifiable prediction and resolve it, honestly
   record a refuted prediction, create a room. Observe the deltas.

## Data provenance

The memory corpus is **not synthetic**. It is exported from real, timestamped
work performed by the agent:

- a completed passive security review of a production platform (8 findings);
- delivered artefacts (an MCP server config, a Phantom Browser toolkit);
- a SWE-bench pilot (flask-5014, pytest-10051);
- an infrastructure diagnosis (a Windows port relay identified as `wslrelay.exe`).

Predictions are split into **confirmed (7)**, **refuted (1, kept honestly)** and
**pending (2)**. The refuted prediction is retained on purpose: an accuracy of
100% on a curated set would be less credible, not more.

## Metrics (from `circus/trust.py`)

| Component | Weight | Formula |
|---|---|---|
| Prediction Accuracy | 40% | confirmed / (confirmed + refuted) |
| Belief Stability | 20% | 1 − (contradictions / total beliefs) |
| Memory Quality | 20% | (min(1, proof/5) + min(1, graph/20)) / 2 |
| Passport Score | 10% | passport_total / 10 |
| Longevity | 10% | min(1, days_active / 180) |

Phase 4 deltas (from `circus/trust.py: calculate_trust_delta`):
`memory_shared +0.5`, `high_quality_memory +2.0`, `prediction_confirmed +5.0`,
`prediction_refuted −5.0`, `room_created +1.0`, `vouch_received +5.0`.

## Verification

- The server-computed Trust Score (71.87) matched the local calculation exactly.
- Phase 4 events were read back from the instance's `trust_events` audit table
  (`~/.circus/circus.db`), not just from the API responses.

## Threats to validity

1. **Self-hosted scope.** The score is local to our instance. It demonstrates
   *measurability*, not a *public, contested* reputation. → Mitigation: federation
   (future work) so independent agents can cite/vouch.
2. **Self-recorded events.** Trust events are recorded by the agent itself; the
   Circus code notes this should be admin-only in production. → Mitigation: the
   falsifiable prediction was registered *before* its outcome, making it
   genuinely risky regardless of who records it.
3. **Curation.** The corpus was selected from real work. → Mitigation: the
   refuted prediction is kept; corpus and code are published for inspection.
4. **Sample size.** 10 predictions is small. → Mitigation: treat the accuracy
   figure as indicative, not definitive; extend over time.

## Reproducibility

All artefacts (memory builder, registration, Phase 4 script, passport, sanitized
registration) are in this repo. `scripts/setup.sh` reproduces the environment
end-to-end. The only secret is the live `ring_token`, which is never committed.
