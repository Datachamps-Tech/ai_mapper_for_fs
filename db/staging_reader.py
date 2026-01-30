# db/staging_reader.py

from sqlalchemy import text
from db.session import engine
from typing import List, Dict, Any, Optional


def fetch_distinct_primary_groups(tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch unclassified primary groups from staging table.
    
    Args:
        tenant_id: If provided, only fetch rows for this tenant.
                   If None, fetch all tenants (batch processing mode).
    
    Returns:
        List of dicts with keys: id, tenant_id, raw_id, primary_group
    """
    # Base query
    query = """
    SELECT DISTINCT
        s.id,
        s.tenant_id,
        s.raw_id,
        s.primary_group
    FROM staging.stg_fs_mapper s
    WHERE s.primary_group IS NOT NULL
      AND TRIM(s.primary_group) <> ''
      AND NOT EXISTS (
          SELECT 1 
          FROM marts.dim_fs d
          WHERE d.stg_id = s.id
      )
    """
    
    # Add tenant filter if provided
    if tenant_id:
        query += " AND s.tenant_id = :tenant_id"
    
    with engine.connect() as conn:
        if tenant_id:
            result = conn.execute(text(query), {"tenant_id": tenant_id})
        else:
            result = conn.execute(text(query))
        
        rows = result.mappings().all()
    
    return rows