from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.core.database import Base
from sqlalchemy.sql import func

class CustomerMetrics(Base):
  __tablename__ = "customer_metrics"

  id = Column(Integer, primary_key=True, index=True)
  message_log_id = Column(Integer, ForeignKey("message_logs.id"), nullable=False, index=True)
  tenant_id = Column(String(50), nullable=False, index=True)
  from_number = Column(String(20), nullable=False, index=True)
  sentiment_score = Column(Integer, default=0)
  has_badwords = Column(Boolean, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())