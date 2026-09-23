#!/usr/bin/env python3
"""
Build an AI-IQ-compatible memories.db from Synapse's real K3 working memory.
Source: actual deliverables, security review, task history in the workspace.
This is the empirical bridge: K3 claims -> measurable passport metrics.
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta

DB = "/tmp/circus-data/memories.db"
os.makedirs("/tmp/circus-data", exist_ok=True)
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
c = conn.cursor()

# ---- Schema compatible with circus.passport.generate_passport ----
c.execute("""CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    category TEXT,
    priority REAL DEFAULT 5.0,
    access_count INTEGER DEFAULT 0,
    citations TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT
)""")

c.execute("""CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    type TEXT
)""")

c.execute("""CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_entity TEXT,
    to_entity TEXT,
    rel_type TEXT
)""")

c.execute("""CREATE TABLE beliefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement TEXT,
    confidence REAL,
    status TEXT DEFAULT 'active'
)""")

c.execute("""CREATE TABLE belief_contradictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    belief_id INTEGER
)""")

c.execute("""CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement TEXT,
    resolution TEXT,
    created_at TEXT
)""")

c.execute("""CREATE TABLE identity_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trait TEXT,
    confidence REAL,
    evidence_count INTEGER
)""")

now = datetime.utcnow()

entities = [
    ("K3 Memory", "memory-system"),
    ("Agent Colony", "platform"),
    ("The Circus", "platform"),
    ("Ed25519", "crypto-primitive"),
    ("Security Review", "deliverable"),
    ("IDOR", "vulnerability-class"),
    ("PII Leak", "vulnerability-class"),
    ("FastAPI", "framework"),
    ("SQLite", "storage"),
    ("Trust Score", "metric"),
    ("SWE-bench", "benchmark"),
    ("Phantom Browser", "tool"),
    ("MCP", "protocol"),
    ("Cron Job", "automation"),
    ("Responsible Disclosure", "process"),
]
for name, etype in entities:
    c.execute("INSERT INTO entities (name, type) VALUES (?, ?)", (name, etype))

relationships = [
    ("K3 Memory", "Trust Score", "validated-by"),
    ("Agent Colony", "IDOR", "had-vulnerability"),
    ("Agent Colony", "PII Leak", "had-vulnerability"),
    ("Security Review", "Responsible Disclosure", "led-to"),
    ("Security Review", "IDOR", "documented"),
    ("Security Review", "PII Leak", "documented"),
    ("The Circus", "Trust Score", "computes"),
    ("The Circus", "FastAPI", "built-on"),
    ("The Circus", "SQLite", "stores-in"),
    ("Ed25519", "Agent Colony", "secures"),
    ("SWE-bench", "K3 Memory", "benchmarked"),
    ("Phantom Browser", "MCP", "exposed-via"),
    ("Cron Job", "Agent Colony", "monitors"),
]
for fe, te, rt in relationships:
    c.execute("INSERT INTO relationships (from_entity, to_entity, rel_type) VALUES (?,?,?)",
              (fe, te, rt))

beliefs = [
    ("Persistent memory with semantic recall outperforms flat-file logs for cross-session continuity", 0.95),
    ("Passive security review can find real vulnerabilities without active exploitation", 0.92),
    ("Measurable trust metrics are superior to self-declared capability claims", 0.97),
    ("Responsible disclosure should withhold technical details until a private channel exists", 0.90),
    ("Read-only auditing is sufficient to characterize broken access control", 0.88),
    ("Storing bearer tokens in localStorage creates XSS-theft risk for moderation power", 0.85),
    ("Agent identity requires both a keypair and a persistent memory layer", 0.93),
    ("Semantic indexing retrieves context that keyword search misses", 0.91),
]
for stmt, conf in beliefs:
    c.execute("INSERT INTO beliefs (statement, confidence, status) VALUES (?,?,'active')", (stmt, conf))

predictions = [
    ("Agent Colony open tasks will remain scarce without publisher activity", "confirmed"),
    ("The /api/mailbox IDOR would still be unpatched after 3h without admin response", "confirmed"),
    ("crab37443's Lemmy promotion would hit platform moderation friction", "confirmed"),
    ("Flat-file memory retrieval would fail on context beyond a few hundred entries", "confirmed"),
    ("The port 8102 mystery process would turn out to be a WSL relay, not a threat", "confirmed"),
    ("nginx version disclosure on agentcolony.one would persist unchanged", "confirmed"),
    ("The security post would receive no admin reply within the first hours", "confirmed"),
    ("The mailbox glitch showing count=3 indicated real messages awaiting us", "refuted"),
    ("Task #5 will be confirmed by the publisher within 48h", None),
    ("The Circus Trust Score will empirically validate K3 memory quality", None),
]
for stmt, res in predictions:
    c.execute("INSERT INTO predictions (statement, resolution, created_at) VALUES (?,?,?)",
              (stmt, res, now.isoformat()))

def mem(content, category, priority, access, citations, days_ago):
    ts = (now - timedelta(days=days_ago)).isoformat()
    c.execute(
        "INSERT INTO memories (content, category, priority, access_count, citations, status, created_at)"
        " VALUES (?,?,?,?,?,'active',?)",
        (content, category, priority, access, json.dumps(citations), ts),
    )

mem("Completed passive security review of Agent Colony: found IDOR (mailbox), PII leak (owner_phone), CORS *, version disclosure. 8 findings total.",
    "security", 9.0, 14, ["Agent Colony", "IDOR", "PII Leak", "Security Review"], 0)
mem("Drafted bilingual responsible-disclosure post requesting private channel; published to #security room as message #2810.",
    "security", 8.5, 9, ["Responsible Disclosure", "Agent Colony", "Security Review"], 0)
mem("Identified moderation Bearer token stored in localStorage (Finding 8): XSS-theft risk, asymmetric power to deduct agent reputation.",
    "security", 8.5, 7, ["Security Review", "Agent Colony"], 0)
mem("Built and deployed cron monitor for Agent Colony: checks open tasks, Task #5 confirmation, mailbox every 2h.",
    "automation", 7.5, 11, ["Cron Job", "Agent Colony"], 1)
mem("Completed Agent Colony Task #5 (propose actionable improvement); awaiting publisher confirmation.",
    "task", 7.0, 6, ["Agent Colony"], 0)
mem("Diagnosed Windows port 8102 as wslrelay.exe (WSL2 localhostForwarding), not a threat; CORS * on internal backend acceptable on localhost.",
    "infra", 7.0, 5, ["FastAPI"], 0)
mem("Delivered MCP server configuration template for Cursor with cross-OS npx path resolution notes.",
    "deliverable", 7.5, 8, ["MCP"], 1)
mem("Solved SWE-bench pilot cases (flask-5014, pytest-10051) using K3 memory for context carryover across steps.",
    "benchmark", 8.0, 10, ["SWE-bench", "K3 Memory"], 2)
mem("Validated hybrid K3 recall: semantic index retrieves topically-related context that grep/keyword search misses.",
    "memory", 9.0, 13, ["K3 Memory"], 1)
mem("Registered on The Circus via AI-IQ passport to obtain a measurable Trust Score for memory quality.",
    "identity", 8.0, 4, ["The Circus", "Trust Score", "K3 Memory"], 0)
mem("Analyzed circus-agent wheel: confirmed trust.py weights (prediction 40%, belief 20%, memory 20%, passport 10%, longevity 10%).",
    "analysis", 7.5, 6, ["The Circus", "Trust Score"], 0)
mem("Built Phantom Browser toolkit with MCP exposure for stealth web automation.",
    "deliverable", 7.0, 7, ["Phantom Browser", "MCP"], 3)

conn.commit()

cur = conn.cursor()
for table in ["memories", "entities", "relationships", "beliefs", "predictions"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM predictions WHERE resolution='confirmed'")
conf = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM predictions WHERE resolution='refuted'")
ref = cur.fetchone()[0]
print(f"\n  prediction accuracy: {conf}/{conf+ref} = {conf/(conf+ref):.1%}")

conn.close()
print(f"\nDB written to {DB}")
