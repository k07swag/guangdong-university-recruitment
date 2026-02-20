#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================="
echo "  广东省高校招聘信息 - 本地服务器"
echo "=========================================="
echo ""
echo "本机访问: http://localhost:8080"
echo ""
# 显示本机局域网 IP，方便同 WiFi 的人访问
IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "（无法获取）")
if [ -n "$IP" ] && [ "$IP" != "（无法获取）" ]; then
  echo "同一 WiFi 下其他人/手机访问: http://${IP}:8080"
  echo ""
fi
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
python3 -m http.server 8080 --bind 0.0.0.0
