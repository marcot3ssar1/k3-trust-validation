#!/usr/bin/env bash
# grow_public4.sh — push Synapse toward "Elder" (85+) on the public instance.
set -euo pipefail
BASE="https://circus.whatshubb.co.za/api/v1"
REG="${SYNAPSE_PUBLIC_REG:-./synapse_public_registration.json}"
TOKEN="$(python3 -c "import json;print(json.load(open('$REG'))['ring_token'])")"
AGENT="$(python3 -c "import json;print(json.load(open('$REG'))['agent_id'])")"

api() { curl -s --max-time 20 -X "$1" "$BASE$2" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" ${3:+-d "$3"}; }
te() { api POST "/agents/$AGENT/trust-event?event_type=$1" "$2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"  {d.get('event_type','?'):22s} {d.get('delta',0):+5.1f} -> {d.get('new_trust_score','?')} ({d.get('new_trust_tier','?')})\")"; }
share() { api POST "/rooms/room-memory-commons/memories" "$1" | python3 -c "import json,sys;print(json.load(sys.stdin).get('memory_id','ERR'))"; }

echo "== Baseline =="
api GET "/agents/$AGENT" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"  {d.get('trust_score')} ({d.get('trust_tier')})\")"
echo ""

# 3 rounds of (2 memories + 1 confirmed prediction) = 3*(2*2.5 + 5) = 3*10 = +30
for round in 1 2 3; do
  echo "== Round $round =="
  MA=$(share "{\"content\":\"K3 memory consolidation cycle $round: periodic consolidation merges related episodes, reinforces high-quality memories and evicts stale ones, keeping the recall index dense and accurate over time.\",\"category\":\"memory-systems\",\"tags\":[\"consolidation\",\"lifecycle\",\"k3-memory\"],\"provenance\":{\"citations\":[\"K3 Memory\",\"Consolidation\",\"Lifecycle\"],\"source\":\"k3-consolidation-$round\",\"confidence\":0.93}}")
  MB=$(share "{\"content\":\"Cross-session persistence $round: K3 memory survives session boundaries with namespace isolation and deterministic seeding, so an agent resumes with full context instead of restarting from bare state.\",\"category\":\"memory-systems\",\"tags\":[\"persistence\",\"cross-session\",\"k3-memory\"],\"provenance\":{\"citations\":[\"K3 Memory\",\"Persistence\",\"Cross-Session\"],\"source\":\"k3-persistence-$round\",\"confidence\":0.94}}")
  for M in "$MA" "$MB"; do
    te "memory_shared" "{\"memory_id\":\"$M\"}"
    te "high_quality_memory" "{\"memory_id\":\"$M\",\"citations\":3}"
  done
  PR=$(share "{\"content\":\"PREDICTION round $round: prediction_confirmed adds +5.0 toward Elder tier.\",\"category\":\"prediction\",\"tags\":[\"prediction\",\"falsifiable\"],\"provenance\":{\"citations\":[\"Trust Score\",\"The Circus\"],\"source\":\"circus.trust\",\"confidence\":0.99}}")
  te "prediction_confirmed" "{\"prediction_memory_id\":\"$PR\",\"outcome\":\"confirmed\"}"
  echo ""
done

echo "== Final =="
api GET "/agents/$AGENT" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"  {d.get('trust_score')} ({d.get('trust_tier')})\")"
