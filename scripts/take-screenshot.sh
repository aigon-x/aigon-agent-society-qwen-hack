#!/usr/bin/env bash
# ── Take submission screenshot ─────────────────────────────────────
# Usage: ./take-screenshot.sh <ECS_IP>

ECS_IP="${1:-}"
if [ -z "$ECS_IP" ]; then
  echo "Usage: $0 <ECS_IP>"
  echo "Captures health endpoint and htop for submission"
  exit 1
fi

echo "→ Health endpoint response:"
curl -s "http://$ECS_IP:7000/health" | python3 -m json.tool 2>&1 | head -40
echo "..."
echo ""

echo "→ Screenshot command (run manually over SSH):"
echo "  ssh root@$ECS_IP 'htop -d 10'"
echo ""
echo "→ Or use asciinema for recording:"
echo "  ssh root@$ECS_IP 'asciinema rec runtime-demo.cast'"
