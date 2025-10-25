from pydantic import BaseModel
# from typing import Optional, List

class MessageIn(BaseModel):
  tenant_id: str
  from_number: str
  to_number: str
  text: str
  message_id: str
  customer_id: int

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
