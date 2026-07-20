#!/usr/bin/env bash
set -euo pipefail

# ── AIGON-X Qwen Hack — Deploy to Alibaba Cloud ECS ────────────────

REGION="ap-southeast-1"
ECS_IP="${1:-}"

if [ -z "$ECS_IP" ]; then
  echo "Usage: $0 <ECS_IP_ADDRESS>"
  echo ""
  echo "Prerequisites:"
  echo "  1. Alibaba Cloud ECS instance (Ubuntu 24.04, ap-southeast-1)"
  echo "  2. Security group: allow :7000, :8080 from 0.0.0.0/0"
  echo "  3. SSH key pair configured"
  echo ""
  echo "Quick ECS setup:"
  echo "  aliyun ecs CreateInstance --RegionId $REGION \\"
  echo "    --InstanceType ecs.g7.xlarge --ImageId ubuntu_24_04_x64_20G_alibase_20250325.vhd"
  exit 1
fi

: "${QWEN_API_KEY:?set QWEN_API_KEY in your environment before running this script}"

BINARY="../runtime-v2/target/release/aigon-runtime-v2"
REMOTE_DIR="/opt/aigon-x-runtime"

echo "→ Stripping binary..."
strip "$BINARY" -o /tmp/aigon-runtime-v2-stripped 2>/dev/null || true

echo "→ Creating remote directory..."
ssh "root@$ECS_IP" "mkdir -p $REMOTE_DIR"

echo "→ Copying binary..."
scp /tmp/aigon-runtime-v2-stripped "root@$ECS_IP:$REMOTE_DIR/"
ssh "root@$ECS_IP" "chmod +x $REMOTE_DIR/aigon-runtime-v2"

echo "→ Creating systemd service..."
ssh "root@$ECS_IP" "cat > /etc/systemd/system/aigon-runtime.service << 'SVC'
[Unit]
Description=AIGON-X Runtime v2 — Agent Society
After=network.target

[Service]
Type=simple
ExecStart=$REMOTE_DIR/aigon-runtime-v2 --mode standalone --listen 0.0.0.0:7000
Environment=RUST_LOG=info
Environment=QWEN_API_KEY=$QWEN_API_KEY
Environment=QWEN_ENDPOINT=https://<your-workspace-id>.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
Environment=QWEN_MODEL=qwen3.7-max
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVC"

echo "→ Starting service..."
ssh "root@$ECS_IP" "systemctl daemon-reload && systemctl enable aigon-runtime && systemctl start aigon-runtime"

echo "→ Waiting for health check..."
for i in $(seq 1 12); do
  if curl -sf "http://$ECS_IP:7000/health" >/dev/null 2>&1; then
    echo "✓ Runtime healthy on http://$ECS_IP:7000"
    break
  fi
  echo "  waiting... ($i/12)"
  sleep 5
done

echo "→ Done! Take screenshot now."
echo "  curl http://$ECS_IP:7000/health | python3 -m json.tool"
