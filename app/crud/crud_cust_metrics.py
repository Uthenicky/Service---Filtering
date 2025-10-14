from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer_metrics import CustomerMetrics
from app.api.schemas import CustomerMetricsIn

async def create_customer_metrics(
  db: AsyncSession, 
  customer_in: CustomerMetricsIn, 
  ):
  customer = CustomerMetrics(
    tenant_id=customer_in.tenant_id,
    message_log_id=customer_in.message_log_id,
    from_number=customer_in.from_number,
    sentiment_score=customer_in.sentiment_score,
    has_badwords=customer_in.has_badwords
  )
  db.add(customer)
  await db.commit()
  await db.refresh(customer)
  return customer