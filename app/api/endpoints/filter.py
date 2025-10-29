from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import schemas
from app.core.database import get_db
from app.services.normalization import SlangNormalizer
from app.services.analysis import analysis_service
from app.crud import background_process

router = APIRouter()

@router.post("/", response_model=schemas.MessageOut, status_code=status.HTTP_202_ACCEPTED)
async def filter_message(
  message_in: schemas.MessageIn,
  background_tasks: BackgroundTasks,
  db: AsyncSession = Depends(get_db)
):
  try:
    normalized_text = SlangNormalizer.normalize(message_in.text)
    sentiment = analysis_service.analyze_sentiment(normalized_text)
    badwords = analysis_service.filter_badwords(normalized_text)
    
    analysis_result = schemas.AnalysisResult(
      sentiment=sentiment,
      badwords=badwords,
      normalized_text=normalized_text
    )
    
    background_tasks.add_task(
      background_process.log_all_data_in_background, 
      db, 
      message_in=message_in, 
      analysis=analysis_result
    )
    
    return schemas.MessageOut(
      original_message=message_in,
      analysis=analysis_result
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Internal server error: {e}"
    )