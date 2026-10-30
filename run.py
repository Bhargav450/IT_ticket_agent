import sys
import os

# 1. Automatically switch to the project's virtualenv python if running with another Python
project_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(project_dir, "venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable != venv_python:
    os.execv(venv_python, [venv_python] + sys.argv)

# 2. Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(project_dir, "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("==================================================================")
    print("  🚀 Starting AegisOps Backend on http://127.0.0.1:8000")
    print("  📖 Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
