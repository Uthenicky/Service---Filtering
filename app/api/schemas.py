from pydantic import BaseModel
from typing import Optional

class MessageIn(BaseModel):
  tenant_id: str
  tenant_url: str
  from_number: str
  to_number: str
  text: str
  message_id: str
  customer_id: int
  start_time: int

class AnalysisResult(BaseModel):
  sentiment: dict
  badwords: dict
  normalized_text: str

class MessageOut(BaseModel):
  original_message: MessageIn
  analysis: AnalysisResult

class CustomerMetricsIn(BaseModel):
  tenant_id: str
  message_log_id: int
  from_number: str
  has_badwords: bool
  sentiment_score: int

class PayloadBotService(BaseModel):
  tenant_id: str
  message_id: Optional[str] = None
  original_message: str
  normalization_message: Optional[str] = None
  whatsapp_number: str
  action: bool
  reply_text: Optional[str] = None
  start_time: int