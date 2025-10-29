import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
# from app.api.endpoints import filter
from app.core.rabbitmq import connect_to_rabbitmq, disconnect_from_rabbitmq
from app.consumers.filter_consumer import run_consumer
from app.services.analysis import load_badwords
from app.services.normalization import init_slang_normalizer
from app.utils.loadMessages import load_messages_callback

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

consumer_task = None
normalizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
  global normalizer, consumer_task
  
  await connect_to_rabbitmq()
  await load_badwords()
  await load_messages_callback()
  
  normalizer = await init_slang_normalizer()
    
  # Jalankan consumer di background task
  if settings.RABBITMQ_URL:
    consumer_task = asyncio.create_task(run_consumer(normalizer))

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

# app.include_router(filter.router, prefix="/api/v1/filter", tags=["Filter"])

@app.get("/health", tags=["Health"])
def read_root():
  return {"status": "ok"}