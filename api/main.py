from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import threading
import time
import os

app = FastAPI(title="AI Mapper API")

# ✅ CORS — keeping your existing policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://datachamp-finance-58111015615.asia-south1.run.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Singleton — loaded ONCE when uvicorn starts, reused forever ----
_mapper = None
_thread_local = threading.local()


@app.on_event("startup")
async def startup_event():
    """
    Runs once when the FastAPI service starts.
    Loads spaCy, SentenceTransformer, training data — everything.
    User never waits for this — it happens in the background at deploy time.
    """
    global _mapper
    from src.mapper import AIMapper

    print("🚀 Loading AI Mapper at startup...")
    start = time.time()
    _mapper = AIMapper()
    _mapper.refresh_training_data()
    print(f"✅ Mapper ready in {time.time() - start:.2f}s")


# ---- DB session per thread (not shared across threads) ----
def _get_thread_session():
    from db.session import SessionLocal
    if not hasattr(_thread_local, "session"):
        _thread_local.session = SessionLocal()
    return _thread_local.session


# ---- Worker: one row per thread ----
def _process_row(row):
    from db.dimfs_writer import insert_dimfs

    primary_group = row["primary_group"]
    try:
        result = _mapper.predict_single(primary_group)

        session = _get_thread_session()
        insert_dimfs(
            session=session,
            stg_id=row["id"],
            raw_id=row["raw_id"],
            tenant_id=row["tenant_id"],
            primary_group=primary_group,
            ai_result=result
        )
        session.commit()
        return {"status": "success", "primary_group": primary_group, "method": result["method_used"]}

    except Exception as e:
        try:
            _get_thread_session().rollback()
        except Exception:
            pass
        return {"status": "failed", "primary_group": primary_group, "error": str(e)}


# ---- Request model ----
class MapperRequest(BaseModel):
    tenant_id: Optional[str] = None


# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok", "mapper_ready": _mapper is not None}


@app.post("/run-mapper")
def run_mapper(request: MapperRequest):
    """
    Classify all pending rows using the already-loaded mapper.
    No subprocess. No cold start. Models already in memory.
    """
    if _mapper is None:
        raise HTTPException(status_code=503, detail="Mapper not ready yet — service is still starting up")

    from db.staging_reader import fetch_distinct_primary_groups

    rows = fetch_distinct_primary_groups(tenant_id=request.tenant_id)
    
    if not rows:
        return {
            "status": "completed",
            "processed": 0,
            "message": "Nothing to classify — all items already mapped"
        }

    MAX_WORKERS = int(os.getenv("AI_MAPPER_WORKERS", 5))
    start = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_process_row, row): row for row in rows}
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.time() - start
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")

    response = {
        "status": "completed",
        "tenant_id": request.tenant_id,
        "processed": len(results),
        "success": success,
        "failed": failed,
        "elapsed_seconds": round(elapsed, 2),
        "throughput_per_sec": round(len(results) / elapsed, 2) if elapsed > 0 else 0
    }

    if failed > 0:
        response["failed_items"] = [
            {"primary_group": r["primary_group"], "error": r["error"]}
            for r in results if r["status"] == "failed"
        ]

    return response


@app.get("/status/{tenant_id}")
def get_status(tenant_id: str):
    """Classification status for a tenant."""
    from db.session import SessionLocal
    from sqlalchemy import text

    session = SessionLocal()
    try:
        total = session.execute(text("""
            SELECT COUNT(*) FROM staging.stg_fs_mapper
            WHERE tenant_id = :tid
              AND primary_group IS NOT NULL
              AND TRIM(primary_group) <> ''
        """), {"tid": tenant_id}).scalar()

        classified = session.execute(text("""
            SELECT COUNT(DISTINCT d.stg_id)
            FROM marts.dim_fs d
            JOIN staging.stg_fs_mapper s ON d.stg_id = s.id
            WHERE s.tenant_id = :tid
        """), {"tid": tenant_id}).scalar()

        pending = total - classified

        return {
            "tenant_id": tenant_id,
            "total_items": total,
            "classified": classified,
            "pending": pending,
            "completion_rate": f"{(classified / total * 100):.1f}%" if total > 0 else "0%"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()