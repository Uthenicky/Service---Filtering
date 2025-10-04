from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from app.core.database import Base
from sqlalchemy.sql import func

class MessageLog(Base):
  __tablename__ = "message_logs"

  id = Column(Integer, primary_key=True, index=True)
  client_id = Column(String, index=True)
  from_number = Column(String, index=True)
  to_number = Column(String, index=True)
  original_text = Column(Text)
  normalized_text = Column(Text)
  sentiment = Column(JSON)
  badwords = Column(JSON)
  created_at = Column(DateTime(timezone=True), server_default=func.now())