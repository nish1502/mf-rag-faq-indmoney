import sys
import os

# Add the parent directory to sys.path so we can import from Phase_8
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase_8.api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
