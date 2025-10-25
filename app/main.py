import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import filter
from app.core.rabbitmq import connect_to_rabbitmq, disconnect_from_rabbitmq
from app.consumers.filter_consumer import run_consumer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

consumer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
  await connect_to_rabbitmq()
  
  # Jalankan consumer di background task
  global consumer_task
  if settings.RABBITMQ_URL:
    consumer_task = asyncio.create_task(run_consumer())

  yield

  logger.error("Application shutdown...")
  if consumer_task and not consumer_task.done():
    consumer_task.cancel()
    try:
      await consumer_task
    except asyncio.CancelledError:
      logger.error("RabbitMQ consumer task cancelled.")
    except Exception as e:
      logger.error(f"Error during consumer task cancellation: {e}")

  await disconnect_from_rabbitmq()
  print("Application shutdown complete.")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(filter.router, prefix="/api/v1/filter", tags=["Filter"])

@app.get("/health", tags=["Health"])
def read_root():
  return {"status": "ok"}