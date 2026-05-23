#!/bin/bash
cd "$(dirname "$0")"
echo "=== Setup Data Analysis System ==="

echo "[1/3] Creating Python virtual environment..."
python3 -m venv venv

echo "[2/3] Installing Python packages..."
./venv/bin/pip install -r backend/requirements.txt -q

echo "[3/3] Installing Node.js packages..."
cd frontend && npm install

echo ""
echo "Setup complete! Run ./start.sh"
