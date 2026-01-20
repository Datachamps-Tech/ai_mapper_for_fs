from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, JSON, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DimFS(Base):
    __tablename__ = "dim_fs"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'primary_group', name='uq_tenant_primary_group'),
        {'schema': 'marts'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    tenant_id = Column(String, nullable=False, index=True)  # ← Add index for faster lookups
    primary_group = Column(String, nullable=False, index=True)  # ← Add index
    
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
    
    # AI metadata
    method_user = Column(String, nullable=True)
    matched_training_low = Column(String, nullable=True)
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