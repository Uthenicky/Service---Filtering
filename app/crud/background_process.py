
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import schemas
from app.crud import crud_cust_metrics, crud_message


async def log_all_data_in_background(db: AsyncSession, message_in: schemas.MessageIn, analysis: schemas.AnalysisResult):
  message_log = await crud_message.create_log(
    db, 
    message_in=message_in, 
    analysis=analysis
  )

  badwords = analysis.badwords
  sentiment = analysis.sentiment
  
  should_create_metric = False
  has_badwords_flag = False
  sentiment_score_val = 0

  if badwords and badwords.get('has_badwords'):
    should_create_metric = True
    has_badwords_flag = True

  if sentiment and sentiment.get('score', 0) != 0:
    should_create_metric = True
    sentiment_score_val = sentiment.get('score', 0)
  
  if should_create_metric:
    customer_in = schemas.CustomerMetricsIn(
      tenant_id=message_in.tenant_id,
      from_number=message_in.from_number,
      message_log_id=message_log.id,
      has_badwords=has_badwords_flag,
      sentiment_score=sentiment_score_val
    )
      
    await crud_cust_metrics.create_customer_metrics(
      db,
      customer_in=customer_in
    )