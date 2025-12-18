#!/usr/bin/env bash
set -euo pipefail

# SMART CITY - Démarrage des serveurs (macOS/Linux)
# Équivalent de start.bat (Windows)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "SMART CITY - Démarrage des serveurs"
echo "======================================"
echo

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Erreur: commande '$1' introuvable."
    return 1
  }
}

PY_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PY_BIN="python"
else
  echo "Erreur: Python n'est pas installé (python3/python introuvable)."
  exit 1
fi

need_cmd npm

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Erreur: dossier backend introuvable: $BACKEND_DIR"
  exit 1
fi
if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "Erreur: dossier frontend introuvable: $FRONTEND_DIR"
  exit 1
fi

mkdir -p "$ROOT_DIR/.logs"

cleanup() {
  echo
  echo "Arrêt des services..."
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${COLLECTOR_PID:-}" ]] && kill -0 "$COLLECTOR_PID" 2>/dev/null; then
    kill "$COLLECTOR_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "[1/3] Démarrage du backend (Python Flask)..."
(
  cd "$BACKEND_DIR"
  "$PY_BIN" api_backend.py
) >"$ROOT_DIR/.logs/backend.log" 2>&1 &
BACKEND_PID=$!

sleep 3

echo "[2/3] Démarrage du collecteur de données..."
(
  cd "$BACKEND_DIR"
  "$PY_BIN" Collecte_donnees.py
) >"$ROOT_DIR/.logs/collecteur.log" 2>&1 &
COLLECTOR_PID=$!

sleep 2

echo
echo "======================================"
echo "Les services sont en cours de démarrage..."
echo "======================================"
echo

echo "Backend API    : http://localhost:5173"
echo "Collecteur     : En cours d'exécution"
echo "Frontend       : http://localhost:5173"
echo
echo "Ouvrez votre navigateur et allez sur:"
echo "http://localhost:5173"
echo
echo "Comptes de test:"
echo "- admin@smartcity.com / admin123"
echo "- marie.dubois@smartcity.com / password123"
echo
echo "Logs:"
echo "- $ROOT_DIR/.logs/backend.log"
echo "- $ROOT_DIR/.logs/collecteur.log"
echo

echo "[3/3] Démarrage du frontend (Vite React)..."
(
  cd "$FRONTEND_DIR"
  if [[ ! -d node_modules ]]; then
    echo "node_modules absent: exécution de 'npm install'..."
    npm install
  fi
  npm run dev
)
