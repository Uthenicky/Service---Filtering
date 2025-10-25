import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.customers import Customer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_customer_by_number(
    db: AsyncSession, tenant_id: str, from_number: str
) -> Optional[Customer]:
  if not tenant_id or not from_number:
    return None
  try:
    stmt = select(Customer).where(
      Customer.tenant_id == tenant_id,
      Customer.from_number == from_number
    )

    result = await db.execute(stmt)
    customer = result.scalars().first()
    return customer
  except Exception as e:
    logger.error(f"Failed to catch customer by number ({tenant_id}, {from_number}): {e}", exc_info=True)
    raise

async def update_customer_badwords_count(
    db: AsyncSession, customer_id: int, count: int
) -> Optional[Customer]:
  if customer_id is None:
    return None
  try:
    customer = await db.get(Customer, customer_id)
    if customer:
      customer.ban_badwords_count = count

      await db.commit()

      await db.refresh(customer)

      return customer
    else:
      return None
  except Exception as e:
    logger.error(
      f"Failed update badwords count customer {customer_id}: {e}", exc_info=True)
    await db.rollback()
    raise

async def ban_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
  if customer_id is None:
    return None
  try:
    customer = await db.get(Customer, customer_id)
    if customer:
      customer.is_ban = True
      customer.ban_badwords_count = 3
      await db.commit()
      await db.refresh(customer)

      return customer
    else:
      return None
  except Exception as e:
    logger.error(f"Gagal update ban customer {customer_id}: {e}", exc_info=True)
    await db.rollback()
    raise