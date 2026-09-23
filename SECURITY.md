# Security Policy

## What is in this repository

Public showcase material: the experiment harness, an exported (non-sensitive)
memory corpus, and results. No live credentials.

## What is NEVER committed

- **ring_token** — the JWT issued by the Circus instance at registration. It is
  a live credential. The copy in `evidence/synapse_registration.json` is
  **redacted**; the real token lives only at runtime (env var `CIRCUS_RING_TOKEN`)
  or in a local `0600` file that is git-ignored.
- Private keys, API keys, GitHub tokens, `.env` files.
- The K3 memory engine source code and the agent's internal prompts (private).

## If you find a secret here

Stop and report it (open an issue or contact the maintainer) so the credential
can be rotated immediately. Do not use it.

## Reporting a vulnerability

Open an issue describing the problem without including exploit material or any
secret. We will respond and coordinate disclosure.
