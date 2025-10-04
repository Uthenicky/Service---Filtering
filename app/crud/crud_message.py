from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message_log import MessageLog
from app.api.schemas import MessageIn, AnalysisResult

async def create_log(db: AsyncSession, *, message_in: MessageIn, analysis: AnalysisResult):
    log_entry = MessageLog(
        client_id=message_in.client_id,
        from_number=message_in.from_number,
        to_number=message_in.to_number,
        original_text=message_in.text,
        normalized_text=analysis.normalized_text,
        sentiment=analysis.sentiment,
        badwords=analysis.badwords
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry