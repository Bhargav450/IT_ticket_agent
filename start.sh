#!/usr/bin/env bash
set -e

echo "=================================================================="
echo "  🚀 Starting AegisOps: Autonomous IT Support Agent (LangGraph)   "
echo "=================================================================="

# Check Python venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r backend/requirements.txt
fi

# Check Ollama
if command -v ollama >/dev/null 2>&1; then
    echo "[✓] Ollama found."
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "[!] Notice: Ollama service is not currently running on port 11434."
        echo "    To run with live local LLM, start Ollama in another terminal:"
        echo "    $ ollama serve"
        echo "    $ ollama pull llama3.2"
        echo "    (The system will automatically use the built-in reasoning engine until Ollama is up)"
    else
        echo "[✓] Ollama local service is active and responsive on http://localhost:11434"
    fi
fi

# Trap SIGINT / SIGTERM to kill background children
cleanup() {
    echo ""
    echo "Shutting down AegisOps services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start FastAPI Backend
echo ""
echo "[*] Launching FastAPI Backend on http://localhost:8000 ..."
PYTHONPATH=backend ./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend health
sleep 2

# Start React Frontend
echo "[*] Launching React Dashboard on http://localhost:5173 ..."
cd frontend
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================================================="
echo "  ✅ AegisOps Command Center is LIVE!"
echo "  🌐 Frontend Dashboard: http://localhost:5173"
echo "  🔌 Backend API Docs:   http://localhost:8000/docs"
echo "  🤖 Agent LLM Engine:   Ollama (llama3.2 / fallback)"
echo "=================================================================="
echo "Press Ctrl+C to stop all services."

wait
