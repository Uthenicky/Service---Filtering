
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import schemas
from app.core.database import get_db
from app.services.normalization import normalizer
from app.services.analysis import analysis_service
from app.crud import crud_message

router = APIRouter()

@router.post("/", response_model=schemas.MessageOut, status_code=status.HTTP_202_ACCEPTED)
async def filter_message(
    message_in: schemas.MessageIn,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Menerima pesan, menjalankan pipeline analisis, menyimpan log di background,
    dan mengembalikan hasil analisis.
    """
    # 1. Slang Normalization
    normalized_text = normalizer.normalize(message_in.text)
    
    # 2. Sentiment & Bad Words Analysis
    sentiment = analysis_service.analyze_sentiment(normalized_text)
    badwords = analysis_service.filter_badwords(normalized_text)
    
    analysis_result = schemas.AnalysisResult(
        sentiment=sentiment,
        badwords=badwords,
        normalized_text=normalized_text
    )
    
    # 3. Simpan log ke DB secara asinkron di background
    # Ini membuat respons API menjadi sangat cepat
    background_tasks.add_task(
        crud_message.create_log, 
        db, 
        message_in=message_in, 
        analysis=analysis_result
    )
    
    # 4. Kembalikan hasil analisis
    return schemas.MessageOut(
        original_message=message_in,
        analysis=analysis_result
    )