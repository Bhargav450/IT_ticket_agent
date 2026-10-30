import sys
import os

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
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
