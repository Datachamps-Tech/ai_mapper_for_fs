# db/staging_reader.py

from sqlalchemy import text
from db.session import engine


STAGING_QUERY = """
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


def fetch_distinct_primary_groups():
    """
    Returns a list of dicts:
    [
        {"id": "...", "tenant_id": "...", "primary_group": "..."},
        ...
    ]
    """
    with engine.connect() as conn:
        result = conn.execute(text(STAGING_QUERY))
        rows = result.mappings().all()

    return rows