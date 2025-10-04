from pydantic import BaseModel
from typing import Optional, List

class MessageIn(BaseModel):
    client_id: str
    from_number: str
    to_number: str
    text: str

class AnalysisResult(BaseModel):
    sentiment: dict
    badwords: dict
    normalized_text: str

class MessageOut(BaseModel):
    original_message: MessageIn
    analysis: AnalysisResult