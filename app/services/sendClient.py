import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
http_client = httpx.AsyncClient()

async def send_callback(url: str, payload: dict) -> bool:
  if not url:
    logger.error("URL not valid.")
    return False
  try:
    response = await http_client.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    # print(f"Callback berhasil dikirim ke {url}. Status: {response.status_code}")
    return True
  except httpx.RequestError as exc:
    logger.error(f"Gagal mengirim callback ke {url}: Request error {exc}")
  except httpx.HTTPStatusError as exc:
    logger.error(f"Gagal mengirim callback ke {url}: Status error {exc.response.status_code} - Response: {exc.response.text}")
  except Exception as exc:
    logger.error(f"Error tidak terduga saat mengirim callback ke {url}: {exc}")
  return False

async def close_http_client():
  await http_client.aclose()