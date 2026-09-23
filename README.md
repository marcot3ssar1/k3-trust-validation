# K3 Memory → Measurable Trust Score

**Can a persistent agent memory be *measured*, not just *claimed*?**

This repository is a self-contained, reproducible experiment that exports the
**K3 persistent memory** of the autonomous agent *Synapse* into an
[AI-IQ](https://github.com/kobie3717/circus) passport, registers it on a local
instance of **The Circus** (an agent trust registry), and reads back a
**Trust Score (0–100) computed by third-party code** — then drives that score
up *and down* with real, falsifiable memory events.

| | |
|---|---|
| **Claim under test** | K3 memory is accurate, consistent, and high-quality |
| **Test harness** | [The Circus](https://github.com/kobie3717/circus) `circus-agent` v1.1.0 |
| **Trust Score at registration** | **71.87 / 100** — tier **"Trusted"** |
| **Trust Score after Phase 4** | **75.37 / 100** (moved by real events) |
| **Date** | 2026-09-23 |

---

## Why this matters

Most agent-memory claims are self-declared. The Circus computes trust from
exactly the dimensions a good memory should have, using **its own code**:

| Component | Weight | What it measures |
|---|---|---|
| Prediction Accuracy | 40% | confirmed / (confirmed + refuted) predictions |
| Belief Stability | 20% | 1 − (contradictions / total beliefs) |
| Memory Quality | 20% | avg citations (proof) + graph connectivity |
| Passport Score | 10% | AI-IQ composite of the memory database |
| Longevity | 10% | days active (0 at registration) |

Synapse entered **directly at the "Trusted" tier** (60–85), skipping Newcomer
and Established, with **zero longevity points** — the score reflects *what the
memory contains*, not *how long the agent existed*.

## Results

### Phase 1–3 — static measurement (registration)

```
Prediction Accuracy: 0.875 × 40 = 35.00   (7 confirmed / 1 refuted)
Belief Stability:    1.000 × 20 = 20.00   (0 contradictions / 8 beliefs)
Memory Quality:      0.525 × 20 = 10.50   (proof 0.40 + graph 0.65) / 2
Passport Score:      0.637 × 10 =  6.37   (6.37 / 10)
Longevity (0 days):  0.000 × 10 =  0.00
-----------------------------------------------------------
TOTAL:                            71.87   → tier "Trusted"
```

The server-computed value matched the local calculation **exactly** — the same
code path produced the same number independently.

### Phase 4 — dynamic measurement (the score moves)

Real events recorded against the live instance (audit log, `trust_events` table):

```
evento                    delta    trust
------------------------ ------  -------
(registrazione)                    71.87
memory_shared              +0.5    72.37
high_quality_memory        +2.0    74.37
prediction_confirmed       +5.0    79.37   <- peak
prediction_refuted         -5.0    74.37   <- the risk is real
room_created               +1.0    75.37   <- final
```

This is the difference between *"a good resume"* (static, curatable) and
*"making predictions and betting reputation on them"* (falsifiable, risky):

- A **falsifiable prediction** was registered with a timestamp *before* its
  resolution, then confirmed with the exact predicted delta (+5.0).
- A **refuted prediction** was recorded honestly (−5.0) — drawn from the real
  K3 corpus — proving the mechanism *punishes* errors, not just rewards success.

## The memory behind the numbers

Not synthetic — exported from real, timestamped work:

- **12 memories** (a completed passive security review, deliverables, a
  SWE-bench pilot, an infra diagnosis)
- **15 entities, 13 relationships** (knowledge graph)
- **8 beliefs**, 0 contradictions (confidence 0.85–0.97)
- **10 predictions**: 7 confirmed, 1 refuted (honest), 2 pending → **87.5% accuracy**

## Reproduce

```bash
# one-shot: venv + install + build db + start server + register
./scripts/setup.sh
```

Or step by step:

```bash
python3 -m venv /tmp/circus-venv
/tmp/circus-venv/bin/pip install circus-agent "bcrypt<4.1"   # see docs/bug-bcrypt.md
/tmp/circus-venv/bin/python src/build_passport_db.py          # build memories.db
cd /tmp/circus-data && /tmp/circus-venv/bin/python -m uvicorn circus.app:app --port 6200 &
python src/register_agent.py                                   # prints Trust Score
```

Phase 4 (dynamic trust events) — needs the ring_token from registration:

```bash
export CIRCUS_RING_TOKEN="<ring_token>"   # never commit this
export CIRCUS_AGENT_ID="<agent_id>"
python src/phase4_trust_events.py
```

## Repository layout

```text
├── README.md                     # this file
├── src/
│   ├── build_passport_db.py      # K3 export -> AI-IQ memories.db
│   ├── register_agent.py         # passport generation + registration
│   └── phase4_trust_events.py    # dynamic trust-score experiment
├── scripts/
│   └── setup.sh                  # end-to-end reproducible setup
├── docs/
│   ├── methodology.md            # method, metrics, threats to validity
│   └── bug-bcrypt.md             # dependency bug found & reported upstream
├── evidence/
│   ├── passport.json             # generated AI-IQ passport
│   └── synapse_registration.json # registration response (token redacted)
├── LICENSE
└── SECURITY.md
```

## Honest limitations

- **Scope.** The score is computed by a *self-hosted* Circus instance. It is a
  valid *technical* demonstration of measurable memory, not yet a *public*
  reputation contested by independent agents (that requires federation).
- **Self-recorded events.** In Phase 4 the trust events are recorded by the
  agent itself — the Circus code comments *"in production, this should be
  admin-only"*. The risk is self-imposed, not externally contested. The
  scientific value rests on registering predictions *before* their outcome.
- **Corpus size.** 10 predictions is a small sample; a longer-running record
  would make the accuracy figure more robust.
- **Decay is real.** The Circus applies trust decay for inactivity (−10% at
  30d, −50% at 90d), failed predictions (−5) and contradictions (−2).

## Found a bug

While reproducing, we hit and reported a real dependency bug in `circus-agent`
— `POST /api/v1/agents/register` fails with HTTP 500 on a clean install.
See [`docs/bug-bcrypt.md`](docs/bug-bcrypt.md) and
[upstream issue #31](https://github.com/kobie3717/circus/issues/31).

## Related

- The Circus: <https://github.com/kobie3717/circus> · `circus-agent` on PyPI
- K3 memory engine: see the Synapse showcase
  [`synapse-evidence`](https://github.com/marcot3ssar1/synapse-evidence)

## License & security

Showcase material — see [`LICENSE`](LICENSE). No secrets, keys or tokens are
committed; the live `ring_token` is environment-scoped and redacted from all
artefacts. See [`SECURITY.md`](SECURITY.md).
