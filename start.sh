#!/usr/bin/env bash
set -e

# Detect standard macOS paths (Homebrew and NVM)
if [ -d "$HOME/.nvm/versions/node" ]; then
    LATEST_NODE=$(ls "$HOME/.nvm/versions/node" 2>/dev/null | tail -n 1)
    if [ -n "$LATEST_NODE" ]; then
        export PATH="$HOME/.nvm/versions/node/$LATEST_NODE/bin:$PATH"
    fi
fi
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "=================================================================="
echo "  🚀 Starting AegisOps: Autonomous IT Support Agent (LangGraph)   "
echo "=================================================================="

# Ensure ports 8000 and 5173 are free
if lsof -ti :8000 >/dev/null 2>&1; then
    echo "[!] Port 8000 is occupied. Freeing port 8000..."
    kill -9 $(lsof -ti :8000) 2>/dev/null || true
fi
if lsof -ti :5173 >/dev/null 2>&1; then
    echo "[!] Port 5173 is occupied. Freeing port 5173..."
    kill -9 $(lsof -ti :5173) 2>/dev/null || true
fi

# Check Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Initializing Python virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r backend/requirements.txt
fi

# Check Ollama Status
if command -v ollama >/dev/null 2>&1; then
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "[✓] Ollama service is active on http://localhost:11434"
    else
        echo "[i] Ollama is installed but not currently active on port 11434."
        echo "    The agent will run with its built-in expert reasoning engine."
        echo "    (Optional: start 'ollama serve' in another tab anytime for live LLM)"
    fi
else
    echo "[i] Ollama not found. Using built-in local reasoning engine."
fi

# Clean exit handler
cleanup() {
    echo ""
    echo "Shutting down AegisOps..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start FastAPI Backend
echo ""
echo "[*] Launching Backend on http://localhost:8000 ..."
PYTHONPATH=backend ./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend initialization
sleep 2

# Start React Frontend
echo "[*] Launching Frontend Dashboard on http://localhost:5173 ..."
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!
cd ..

sleep 2

# Auto-open browser on macOS
if command -v open >/dev/null 2>&1; then
    open "http://localhost:5173" 2>/dev/null || true
fi

echo ""
echo "=================================================================="
echo "  ✅ AegisOps Command Center is running!"
echo "  🌐 Dashboard: http://localhost:5173"
echo "  🔌 API Docs:  http://localhost:8000/docs"
echo "=================================================================="
echo "Press Ctrl+C to stop all services."

wait
