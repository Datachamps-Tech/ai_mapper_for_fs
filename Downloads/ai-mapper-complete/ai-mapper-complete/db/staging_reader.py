# db/staging_reader.py

from sqlalchemy import text
from db.session import engine
from typing import List, Dict, Any, Optional


def fetch_distinct_primary_groups(tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch unclassified primary groups from staging table.
    Deduplication: skip if (tenant_id + primary_group) already exists in dim_fs.
    Within staging itself, only take one row per (tenant_id + primary_group) combo.
    """
    query = """
    SELECT DISTINCT ON (s.tenant_id, s.primary_group)
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
          WHERE d.tenant_id = s.tenant_id
            AND LOWER(TRIM(d.primary_group)) = LOWER(TRIM(s.primary_group))
      )
    """

    if tenant_id:
        query += " AND s.tenant_id = :tenant_id"

    with engine.connect() as conn:
        if tenant_id:
            result = conn.execute(text(query), {"tenant_id": tenant_id})
        else:
            result = conn.execute(text(query))

        rows = result.mappings().all()

    return rows