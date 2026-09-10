#!/bin/sh
set -eu

cd /var/www/html

php artisan config:clear || true
php artisan migrate --force || true
php artisan db:seed --force || true

php artisan schedule:work &
SCHEDULE_PID=$!

start_serve() {
  php artisan serve --host=0.0.0.0 --port=8080 &
  SERVE_PID=$!
  # php artisan serve spawna o php -S; aguarda subir
  sleep 1
}

stop_serve() {
  if [ -n "${SERVE_PID:-}" ]; then
    kill "$SERVE_PID" 2>/dev/null || true
    # mata o php -S filho se ainda estiver vivo
    pkill -f "0.0.0.0:8080" 2>/dev/null || true
    wait "$SERVE_PID" 2>/dev/null || true
  fi
}

trap 'stop_serve; kill "$SCHEDULE_PID" 2>/dev/null || true; exit 0' INT TERM

start_serve

falhas=0
while true; do
  sleep 15
  if curl -fsS --connect-timeout 2 --max-time 3 "http://127.0.0.1:8080/healthz" >/dev/null 2>&1; then
    falhas=0
    continue
  fi
  falhas=$((falhas + 1))
  echo "[watchdog] painel sem resposta (falha $falhas)" >&2
  if [ "$falhas" -ge 2 ]; then
    echo "[watchdog] reiniciando php artisan serve..." >&2
    stop_serve
    sleep 1
    start_serve
    falhas=0
  fi
done
