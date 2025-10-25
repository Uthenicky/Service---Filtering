from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.database import Base
from sqlalchemy.sql import func

class Customer(Base):
  __tablename__ = "customers"

  id = Column(Integer, primary_key=True)
  tenant_id = Column(String(50), nullable=False)
  from_number = Column(String(20), nullable=False)
  customer_name = Column(String(200))
  is_ban = Column(Boolean, default=False)
  ban_reply_count = Column(Integer, default=0)
  ban_badwords_count = Column(Integer, default=0)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())