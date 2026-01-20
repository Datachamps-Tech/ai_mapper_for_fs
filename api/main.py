from fastapi import FastAPI
import subprocess

app = FastAPI(title="AI Mapper API")

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
