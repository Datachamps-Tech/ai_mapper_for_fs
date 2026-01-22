from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI(title="AI Mapper API")

# ✅ CORS configuration
origins = [
    "https://datachamp-finance-58111015615.asia-south1.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Whitelisted frontend
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, OPTIONS
    allow_headers=["*"],          # Content-Type, Authorization, etc.
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run-mapper")
def run_mapper():
    """
    This will run your existing script exactly as you do locally.
    """
    try:
        subprocess.run(
            ["python", "run_ai_mapper_db.py"],
            check=True
        )
        return {"status": "completed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
