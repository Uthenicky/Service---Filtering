from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base
from sqlalchemy.sql import func

class ErrorLog(Base):
  __tablename__ = "error_logs"

  id = Column(Integer, primary_key=True, index=True)
  tenant_id = Column(String, index=True)
  request_payload = Column(JSON)
  # Catat di langkah mana error terjadi
  error_step = Column(String)
  error_message = Column(Text)
  created_at = Column(DateTime(timezone=True), server_default=func.now())