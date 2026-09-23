#!/usr/bin/env bash
#
# setup.sh — spin up a local Circus instance and validate K3 memory end-to-end.
#
# Usage:
#   ./scripts/setup.sh
#
# What it does:
#   1. creates a venv (on a native filesystem — /tmp — not a slow mount)
#   2. installs circus-agent + the bcrypt workaround (see docs/bug-bcrypt.md)
#   3. builds the AI-IQ memories.db from the K3 export
#   4. starts the Circus server on 127.0.0.1:6200
#   5. registers the agent and prints the Trust Score
#
set -euo pipefail

VENV="${VENV:-/tmp/circus-venv}"
DATA="${DATA:-/tmp/circus-data}"
PORT="${PORT:-6200}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> [1/5] venv at $VENV"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
# bcrypt<4.1: passlib 1.7.4 is incompatible with bcrypt>=4.1 (see docs/bug-bcrypt.md)
"$VENV/bin/pip" install --quiet circus-agent "bcrypt<4.1"

echo "==> [2/5] build memories.db from K3 export"
mkdir -p "$DATA"
"$VENV/bin/python" "$HERE/src/build_passport_db.py"

echo "==> [3/5] start Circus server on 127.0.0.1:$PORT"
cd "$DATA"
nohup "$VENV/bin/python" -m uvicorn circus.app:app --host 127.0.0.1 --port "$PORT" \
  > /tmp/circus-server.log 2>&1 &
echo "    server PID $! — log: /tmp/circus-server.log"
sleep 6

echo "==> [4/5] health check"
curl -s --max-time 8 "http://127.0.0.1:$PORT/" | python3 -m json.tool | head -5

echo "==> [5/5] generate passport + register"
"$VENV/bin/python" "$HERE/src/register_agent.py" --venv "$VENV" --data "$DATA" --port "$PORT"

echo ""
echo "Done. Trust Score printed above. Evidence in $DATA and ./evidence/."
echo "To run Phase 4 (dynamic trust events):"
echo "  export CIRCUS_RING_TOKEN=<ring_token from registration>"
echo "  export CIRCUS_AGENT_ID=<agent_id from registration>"
echo "  $VENV/bin/python $HERE/src/phase4_trust_events.py"
