import asyncio
import json
import aio_pika
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.normalization import normalizer
from app.services.analysis import analysis_service
from app.crud import background_process, customers
from app.api import schemas
from app.core.rabbitmq import get_rabbitmq_channel
from app.utils.helper import dynamic_messages
from app.utils.loadMessages import get_messages_from_redis
from app.services.sendClient import send_callback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_filtering_task(message: aio_pika.abc.AbstractIncomingMessage):
  async with message.process():
    try:
      payload = json.loads(message.body.decode())
      print(f"Payload: {payload}")

      required_keys = ['tenant_id', 'from_number', 'to_number', 'text']
      if not all(key in payload for key in required_keys):
        print("Invalid payload, missing required keys. Message rejected.")
        return

      message_in_schema = schemas.MessageIn(**payload)
      normalized_text = normalizer.normalize(message_in_schema.text)
      sentiment = analysis_service.analyze_sentiment(normalized_text)
      badwords = analysis_service.filter_badwords(normalized_text)
      
      analysis_result = schemas.AnalysisResult(
        sentiment=sentiment,
        badwords=badwords,
        normalized_text=normalized_text
      )

      from_number = payload.get("from_number")
      tenant_id = payload.get("tenant_id")
      db_session = AsyncSessionLocal()
      
      if badwords.get("has_badwords"):
        badwords_count_max = int(settings.BADWORDS_COUNT_MAX)
        Customer = await customers.get_customer_by_number(db_session, tenant_id=tenant_id, from_number=from_number)
        
        if(Customer):
          count_badwords = Customer.ban_badwords_count or 0
          count_badwords+=1
          
          if(count_badwords < badwords_count_max):
            await customers.update_customer_badwords_count(db_session, customer_id=Customer.id, count=count_badwords)
        
          if(count_badwords >= badwords_count_max):
            await customers.ban_customer(db_session, customer_id=Customer.id)
            
          message_badwords_list = get_messages_from_redis()
          message_badwords = message_badwords_list.get('messages', {}).get('handleBadwords', [])
          reply_message = dynamic_messages(message_badwords, None)
          # print(reply_message)
          return reply_message
        
      if len(sentiment["negative_words"]) > 0:
        message_sentiment_list = get_messages_from_redis()
        message_sentiment = message_sentiment_list.get('messages', {}).get('handleSentiment', [])
        reply_message = dynamic_messages(message_sentiment, None)
        # print(reply_message)
        await send_callback(
          url="http://localhost:3000/send-message",
          payload={
            "number": from_number,
            "message": reply_message
          }
        )
      
      if sentiment["score"] > 0:
        message_sentiment_positif = get_messages_from_redis()
        message_sentiment_positif = message_sentiment_positif.get('messages', {}).get('handlePositiveSentiment', [])
        reply_message = dynamic_messages(message_sentiment_positif, None)
        # print(reply_message)
        
        await send_callback(
          url="http://localhost:3000/send-message",
          payload={
            "number": from_number,
            "message": reply_message
          }
        ) 

      async with AsyncSessionLocal() as db_session:
        try:
          await background_process.log_all_data_in_background(
            db_session,
            message_in=message_in_schema,
            analysis=analysis_result
          )
          # print("Log saved to database.")
        except Exception as db_err:
          logger.error(f"Failed to save log to database: {db_err}")
          
      print("Message processed successfully.")
      return
    except json.JSONDecodeError:
      logger.error("Failed to decode message body (not valid JSON). Message rejected.")
    except Exception as e:
      logger.error(f"Error processing message: {e}")

async def run_consumer():
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

    await queue.consume(process_filtering_task)
    await asyncio.Future()

  except Exception as e:
    logger.error(f"Error in consumer setup or during consumption: {e}")
  finally:
    logger.error("Consumer shutting down...")