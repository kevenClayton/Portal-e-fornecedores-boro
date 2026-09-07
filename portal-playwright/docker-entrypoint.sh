#!/usr/bin/env bash
set -euo pipefail

export DISPLAY="${DISPLAY:-:99}"

# Limpa lock residual (ex.: docker restart sem matar o Xvfb antigo)
rm -f "/tmp/.X${DISPLAY#:}-lock" /tmp/.X11-unix/X"${DISPLAY#:}" 2>/dev/null || true
pkill -f "Xvfb ${DISPLAY}" 2>/dev/null || true
sleep 0.3

# Chromium headed precisa de display virtual no Docker.
# Nao usar só "& + exec": o exec substitui o shell e o Xvfb morre (SIGHUP).
Xvfb "$DISPLAY" -screen 0 1366x768x24 -nolisten tcp -ac >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!
disown "$XVFB_PID" 2>/dev/null || true
sleep 1

if ! kill -0 "$XVFB_PID" 2>/dev/null; then
  echo "Falha ao iniciar Xvfb:" >&2
  cat /tmp/xvfb.log >&2 || true
  exit 1
fi

exec python run.py
