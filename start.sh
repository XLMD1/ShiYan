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
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Ctrl+C to stop both"

trap "kill $DJANGO_PID $VUE_PID 2>/dev/null; exit" INT
wait
