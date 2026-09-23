# Dependency bug: missing `bcrypt` backend

While reproducing this experiment on a clean install, agent registration failed
with HTTP 500. Reported upstream as
[**circus issue #31**](https://github.com/kobie3717/circus/issues/31).

## Symptom

```
POST /api/v1/agents/register  ->  HTTP 500 Internal Server Error
passlib.exc.MissingBackendError: bcrypt: no backends available --
recommend you install one (e.g. 'pip install bcrypt')
```

Traceback points to `circus/routes/agents.py`:

```python
token_hash = bcrypt.hash(ring_token_value)
```

## Root cause

`circus-agent` 1.1.0 declares `passlib>=1.7.4` but **not** a `bcrypt` backend.
passlib needs the external `bcrypt` package, which is not installed.

Verified from the wheel metadata (`circus_agent-1.1.0.dist-info/METADATA`):

```
Requires-Dist: passlib>=1.7.4
# (no bcrypt)
```

## Workaround (confirmed)

```bash
pip install "bcrypt<4.1"
```

**Pin matters:** passlib 1.7.4 reads `bcrypt.__about__.__version__`, removed in
bcrypt 4.1+. Installing a newer bcrypt causes a second, distinct failure
(`AttributeError: module 'bcrypt' has no attribute '__about__'`). `bcrypt<4.1`
avoids both.

## Suggested upstream fix

```toml
dependencies = [
    "passlib>=1.7.4",
    "bcrypt>=4.0.1,<4.1",
]
```

Or migrate from passlib to calling `bcrypt` directly.

## Status

- [x] Reproduced on clean install
- [x] Workaround confirmed (registration succeeds, trust score computed)
- [x] Reported upstream (issue #31)
- [ ] Fixed in a release
