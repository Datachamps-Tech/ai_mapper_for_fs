from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import subprocess
import os

app = FastAPI(title="AI Mapper API")

# ✅ CORS configuration (keeping your existing policy)
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


class MapperRequest(BaseModel):
    """Request model for mapper endpoint"""
    tenant_id: Optional[str] = None  # If None, process all tenants


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/run-mapper")
def run_mapper(request: MapperRequest):
    """
    Run AI mapper for specified tenant or all tenants.
    
    Args:
        tenant_id: Optional tenant identifier. If not provided, processes all unclassified rows.
    
    Returns:
        Status and summary of processing
    """
    try:
        # Build command
        cmd = ["python", "run_ai_mapper_db.py"]
        
        # Set environment variable for tenant_id if provided
        env = os.environ.copy()
        if request.tenant_id:
            env["TENANT_ID"] = request.tenant_id
        
        # Run the mapper script
        result = subprocess.run(
            cmd,
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        
        return {
            "status": "completed",
            "tenant_id": request.tenant_id,
            "message": "AI mapping completed successfully",
            "output": result.stdout[-500:] if result.stdout else ""  # Last 500 chars
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(e),
                "stderr": e.stderr[-500:] if e.stderr else ""
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "error": str(e)
            }
        )


@app.get("/status/{tenant_id}")
def get_status(tenant_id: str):
    """
    Get classification status for a tenant.
    
    Args:
        tenant_id: Tenant identifier
    
    Returns:
        Summary of classified and pending items
    """
    from db.session import SessionLocal
    from sqlalchemy import text
    
    session = SessionLocal()
    
    try:
        # Count total staging rows for tenant
        total_query = text("""
            SELECT COUNT(*) as total
            FROM staging.stg_fs_mapper
            WHERE tenant_id = :tenant_id
              AND primary_group IS NOT NULL
              AND TRIM(primary_group) <> ''
        """)
        total_result = session.execute(total_query, {"tenant_id": tenant_id}).fetchone()
        total = total_result[0] if total_result else 0
        
        # Count classified rows
        classified_query = text("""
            SELECT COUNT(DISTINCT d.stg_id) as classified
            FROM marts.dim_fs d
            JOIN staging.stg_fs_mapper s ON d.stg_id = s.id
            WHERE s.tenant_id = :tenant_id
        """)
        classified_result = session.execute(classified_query, {"tenant_id": tenant_id}).fetchone()
        classified = classified_result[0] if classified_result else 0
        
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