import httpx
import logging
from app.utils.helper import dynamic_messages
from app.api import schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_callback(url: str, payload: dict) -> bool:
  if not url:
    logger.error("URL not valid.")
    return False
  try:
    async with httpx.AsyncClient() as client:
      response = await client.post(url, json=payload, timeout=10.0)
      response.raise_for_status()
      return True
  except httpx.RequestError as exc:
    logger.error(f"Gagal mengirim callback ke {url}: Request error {exc}")
  except httpx.HTTPStatusError as exc:
    logger.error(f"Gagal mengirim callback ke {url}: Status error {exc.response.status_code} - Response: {exc.response.text}")
  except Exception as exc:
    logger.error(f"Error tidak terduga saat mengirim callback ke {url}: {exc}")
  return False


async def reply(tenant_url, tenant_id, msg_in, from_number, timestamp, message_key, all_messages):
  message_list = all_messages.get('messages', {}).get(message_key, [])
  reply_message = dynamic_messages(message_list, None)

  payload = schemas.PayloadBotService(
    tenant_id=tenant_id,
    original_message=msg_in,
    whatsapp_number=from_number,
    action=True,
    reply_text=reply_message,
    start_time=timestamp
  ).model_dump()

  await send_callback(url=tenant_url, payload=payload)
  return reply_message
