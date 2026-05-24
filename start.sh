#!/bin/bash
cd "$(dirname "$0")"
echo "=== Start Data Analysis System ==="

echo "Starting Django backend..."
./venv/bin/python backend/manage.py runserver 8000 &
DJANGO_PID=$!

echo "Starting Vue frontend..."
cd frontend && npm run dev &
VUE_PID=$!

echo ""
echo "=============================="
echo "  Frontend:    http://localhost:5173"
echo "  Backend API: http://localhost:8000/api/"
echo "  Admin:       http://localhost:8000/admin/"
echo "=============================="
echo ""
echo "Opening http://localhost:5173 ..."
open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null || echo "Please open http://localhost:5173 manually"
echo ""
echo "Ctrl+C to stop both"

trap "kill $DJANGO_PID $VUE_PID 2>/dev/null; exit" INT
wait
