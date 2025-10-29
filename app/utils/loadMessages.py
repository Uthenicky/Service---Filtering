import os
import json
import logging
import asyncio
from redis import asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

MESSAGES_CALLBACK = {}
dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'dictMessages.json')


async def load_messages_callback():
  """Memuat messages dari Redis atau file lokal jika belum ada"""
  global MESSAGES_CALLBACK

  try:
    cached_json = await redis_client.get("messages")

    if cached_json:
      try:
        MESSAGES_CALLBACK = json.loads(cached_json)
        print("✅ Kamus Messages dimuat dari Redis.")
        return
      except json.JSONDecodeError:
        logger.error("Error decode JSON dari Redis. Memuat dari file...")
        MESSAGES_CALLBACK = {}

    if not MESSAGES_CALLBACK:
      if not os.path.exists(dict_path):
        logger.error("File dictMessages.json tidak ditemukan.")
        return

      with open(dict_path, "r", encoding="utf-8") as f:
        MESSAGES_CALLBACK = json.load(f)

      if MESSAGES_CALLBACK:
        await redis_client.set("messages", json.dumps(MESSAGES_CALLBACK))
        print("✅ Kamus Messages disimpan ke Redis.")
      else:
        logger.error("File dictMessages.json kosong atau tidak valid.")

  except Exception as e:
    logger.error(f"Error tidak terduga saat memuat messages: {e}")
    MESSAGES_CALLBACK = {}


async def get_messages_from_redis():
  """Mengambil messages dari Redis"""
  try:
    cached_json = await redis_client.get("messages")
    if cached_json:
      return json.loads(cached_json)
    else:
      logger.warning("Tidak ada messages di Redis.")
      return {}
  except json.JSONDecodeError:
    logger.error("Gagal parse data dari Redis (bukan JSON valid).")
    return {}
  except Exception as e:
    logger.error(f"Error tidak terduga saat mengambil dari Redis: {e}")
    return {}


async def close_redis():
  """Tutup koneksi Redis dengan aman"""
  await redis_client.close()
  await redis_client.connection_pool.disconnect()


# Inisialisasi (jika dijalankan standalone)
# if __name__ == "__main__":
#   asyncio.run(load_messages_callback())
