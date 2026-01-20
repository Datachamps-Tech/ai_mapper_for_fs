from sqlalchemy.dialects.postgresql import insert
from db.models import DimFS
from db.utils import clean_nan
from datetime import datetime

def insert_dimfs(session, tenant_id, primary_group, ai_result):
    """
    Insert new classification result. Skip if (tenant_id, primary_group) already exists.
    Uses PostgreSQL ON CONFLICT DO NOTHING - atomic and safe.
    """
    clean_result = clean_nan(ai_result)
    
    stmt = insert(DimFS).values(
        tenant_id=tenant_id,
        primary_group=primary_group,
        fs=clean_result.get("fs"),
        predicted_fs=clean_result.get("predicted_fs"),
        confidence=clean_result.get("confidence"),
        bs_main_category=clean_result.get("bs_main_category"),
        bs_classification=clean_result.get("bs_classification"),
        bs_sub_classification=clean_result.get("bs_sub_classification"),
        bs_sub_classification_2=clean_result.get("bs_sub_classification_2"),
        pl_classification=clean_result.get("pl_classification"),
        pl_sub_classification=clean_result.get("pl_sub_classification"),
        pl_classification_1=clean_result.get("pl_classification_1"),
        cf_classification=clean_result.get("cf_classification"),
        cf_sub_classification=clean_result.get("cf_sub_classification"),
        expense_type=clean_result.get("expense_type"),
        method_user=clean_result.get("method_used"),
        matched_training_low=clean_result.get("matched_training_row"),
        matched_row_full=clean_result.get("matched_row_full"),
        needs_review=clean_result.get("needs_review"),
        low_confidence_alternative=clean_result.get("low_confidence_alternative"),
        reasoning=clean_result.get("reasoning"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ).on_conflict_do_nothing(
        index_elements=['tenant_id', 'primary_group']
    )
    
    session.execute(stmt)