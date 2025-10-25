import asyncio
import aio_pika
import json
import logging
from typing import Optional, Any
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection: Optional[aio_pika.RobustConnection] = None
channel: Optional[aio_pika.abc.AbstractChannel] = None

def _handle_connection_close(sender: Any, *args: Any, exception: Optional[Exception] = None):
  global connection, channel
  if exception:
    logger.error(f"RabbitMQ connection error/closed unexpectedly: {exception}")
  else:
    logger.error("RabbitMQ connection closed.")
  
  connection = None
  channel = None
  # Di sini bisa ditambahkan logika notifikasi atau percobaan reconnect terjadwal jika diperlukan

async def connect_to_rabbitmq():
  global connection, channel
  if not settings.RABBITMQ_URL:
    logger.error("RABBITMQ_URL not set. RabbitMQ consumer disabled.")
    return

  loop = asyncio.get_running_loop()
  print("Connecting to RabbitMQ...")
  try:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, loop=loop)
    channel = await connection.channel()
    connection.close_callbacks.add(_handle_connection_close)
    print("RabbitMQ Started")

  except Exception as e:
    logger.error(f"Failed to connect to RabbitMQ: {e}")
    await asyncio.sleep(5)
    raise

async def disconnect_from_rabbitmq():
  global connection, channel

  if connection and _handle_connection_close in connection.close_callbacks:
    connection.close_callbacks.remove(_handle_connection_close)

  if channel and not channel.is_closed:
    try:
      await channel.close()
    except Exception as e:
      logger.error(f"Error closing channel: {e}")
      
  if connection and not connection.is_closed:
    try:
      await connection.close()
    except Exception as e:
      logger.error(f"Error closing connection: {e}")
  connection = None
  channel = None

async def get_rabbitmq_channel() -> Optional[aio_pika.abc.AbstractChannel]:
  """Returns the active RabbitMQ channel."""
  # Bisa ditambahkan: Jika channel None atau closed, coba reconnect/initiate connection
  return channel

async def publish_message(queue_name: str, message_body: dict):
  ch = await get_rabbitmq_channel()
  if not ch or ch.is_closed: 
    logger.error("Cannot publish message, channel not available or closed.")
    return False 
  try:
    await ch.declare_queue(queue_name, durable=True)
    # Agar pesan survive restart
    await ch.default_exchange.publish(
      aio_pika.Message(
        body=json.dumps(message_body).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
      ),
      routing_key=queue_name,
    )
    return True
  except Exception as e:
    logger.error(f"Failed to publish message to '{queue_name}': {e}")
    return False