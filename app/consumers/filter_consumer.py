import asyncio
import json
import aio_pika
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.analysis import analysis_service
from app.crud import background_process, customers
from app.api import schemas
from app.core.rabbitmq import get_rabbitmq_channel
from app.utils.loadMessages import get_messages_from_redis
from app.services.sendClient import send_callback, reply

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_filtering_task(message: aio_pika.abc.AbstractIncomingMessage, normalizer):
  async with message.process():
    try:
      payload = json.loads(message.body.decode())
      # print(f"Payload: {payload}")

      required_keys = ['tenant_id', 'tenant_url', 'from_number', 'to_number', 'text', 'start_time']
      if not all(key in payload for key in required_keys):
        logger.error("Invalid payload, missing required keys. Message rejected.")
        return

      message_in_schema = schemas.MessageIn(**payload)
      original_message = message_in_schema.text

      normalized_text = await asyncio.to_thread(normalizer.normalize, text=original_message)
      sentiment = await analysis_service.analyze_sentiment(text=normalized_text)
      badwords = await analysis_service.filter_badwords(text=normalized_text)
      
      analysis_result = schemas.AnalysisResult(
        sentiment=sentiment,
        badwords=badwords,
        normalized_text=normalized_text
      )
      
      async with AsyncSessionLocal() as db:
        try:
          await background_process.log_all_data_in_background(
            db,
            message_in=message_in_schema,
            analysis=analysis_result
          )
        except Exception as db_err:
          logger.error(f"Failed to save log to database: {db_err}")

      from_number = message_in_schema.from_number
      tenant_id = message_in_schema.tenant_id
      tenant_url = message_in_schema.tenant_url
      start_time = message_in_schema.start_time
      all_messages = await get_messages_from_redis()
      
      async with AsyncSessionLocal() as db:
        if badwords.get("has_badwords"):
          badwords_limit = int(settings.BADWORDS_COUNT_MAX)
          customer = await customers.get_customer_by_number(
            db, tenant_id=tenant_id, from_number=from_number
          )

          if customer:
            count = (customer.ban_badwords_count or 0) + 1

            if count < badwords_limit:
              await customers.update_customer_badwords_count(
                db, customer_id=customer.id, count=count
              )
            else:
              await customers.ban_customer(db, customer_id=customer.id)

          await reply(
            tenant_url, tenant_id, original_message, from_number, start_time, "handleBadwords", all_messages
          )
          return

        if sentiment.get("negative_words"):
          await reply(
            tenant_url, tenant_id, original_message, from_number, start_time, "handleSentiment", all_messages
          )

        elif sentiment.get("score", 0) > 0:
          await reply(
            tenant_url, tenant_id, original_message, from_number, start_time, "handlePositiveSentiment", all_messages
          )

        else:
          await send_callback(
            url=tenant_url,
            payload=schemas.PayloadBotService(
              tenant_id=tenant_id,
              original_message=original_message,
              whatsapp_number=from_number,
              action=False,
              normalization_message=normalized_text,
              start_time=start_time
            ).model_dump()
          )

    except json.JSONDecodeError:
      logger.error("Failed to decode message body (not valid JSON). Message rejected.")
    except Exception as e:
      logger.error(f"Error processing message: {e}")

async def run_consumer(normalizer):
  channel = await get_rabbitmq_channel()
  if not channel:
    logger.error("Cannot start consumer, RabbitMQ channel not available.")
    return

  try:
    # Pastikan queue bertahan jika RabbitMQ restart
    queue = await channel.declare_queue(
      settings.FILTERING_QUEUE,
      durable=True
    )
    print(f"Listening for messages on queue '{settings.FILTERING_QUEUE}'...")
    await queue.consume(lambda msg: process_filtering_task(msg, normalizer))
    # await queue.consume(process_filtering_task)
    await asyncio.Future()

  except Exception as e:
    logger.error(f"Error in consumer setup or during consumption: {e}")
  finally:
    logger.error("Consumer shutting down...")