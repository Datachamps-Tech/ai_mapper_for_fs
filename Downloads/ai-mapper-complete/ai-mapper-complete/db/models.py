from sqlalchemy import (
    Column, String, DateTime, Float, Boolean, JSON, Integer, text,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DimFS(Base):
    __tablename__ = "dim_fs"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'primary_group', name='uq_dimfs_tenant_primary_group'),
        {'schema': 'marts'}
    )

    # PRIMARY KEY - auto-generated UUID
    mart_id = Column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    raw_id = Column(Integer, nullable=False, index=True)
    stg_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    primary_group = Column(String, nullable=False, index=True)

    fs = Column(String, nullable=True)
    predicted_fs = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    bs_main_category = Column(String, nullable=True)
    bs_classification = Column(String, nullable=True)
    bs_sub_classification = Column(String, nullable=True)
    bs_sub_classification_2 = Column(String, nullable=True)

    pl_classification = Column(String, nullable=True)
    pl_sub_classification = Column(String, nullable=True)
    pl_classification_1 = Column(String, nullable=True)

    cf_classification = Column(String, nullable=True)
    cf_sub_classification = Column(String, nullable=True)

    expense_type = Column(String, nullable=True)

    method_used = Column(String, nullable=True)
    matched_training_row = Column(String, nullable=True)
    matched_row_full = Column(JSON, nullable=True)

    needs_review = Column(Boolean, nullable=True)
    low_confidence_alternative = Column(String, nullable=True)
    reasoning = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )