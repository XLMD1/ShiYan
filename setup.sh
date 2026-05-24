#!/bin/bash
cd "$(dirname "$0")"
echo "=== Setup Data Analysis System ==="

if [ -f "venv/bin/python" ]; then
  echo "[1/4] venv already exists, skipping..."
else
  echo "[1/4] Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "[2/4] Installing Python packages..."
./venv/bin/pip install -r backend/requirements.txt -q

if [ -d "frontend/node_modules" ]; then
  echo "[3/4] node_modules already exists, skipping..."
else
  echo "[3/4] Installing Node.js packages..."
  cd frontend && npm install
fi

echo "[4/4] Setting up database..."
./venv/bin/python backend/manage.py migrate --run-syncdb

echo ""
echo "Setup complete! Run ./start.sh"
