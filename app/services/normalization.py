import json
import os
import asyncio
import logging
from redis import asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlangNormalizer:
  def __init__(self, dict_path: str, redis_client: aioredis.Redis, redis_key: str = "slang_dict"):
    self.dictionary = {}
    self.redis_client = redis_client
    self.redis_key = redis_key
    self.dict_path = dict_path

  async def load_dictionary(self):
    """Muat kamus slang dari Redis, atau fallback ke file lokal"""
    try:
      cached_dict = await self.redis_client.get(self.redis_key)
      if cached_dict:
        self.dictionary = json.loads(cached_dict)
        logger.info(f"✅ Kamus slang dimuat dari Redis ({len(self.dictionary)} entri).")
        return

      # Kalau Redis kosong, baca dari file
      if os.path.exists(self.dict_path):
        async with asyncio.Lock():  # hindari race read file
          with open(self.dict_path, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)

        logger.info(f"Kamus slang dibaca dari file ({len(self.dictionary)} entri).")

        # Simpan ke Redis
        await self.redis_client.set(self.redis_key, json.dumps(self.dictionary))
        logger.info("Kamus slang disimpan ke Redis.")
      else:
        logger.warning("File slang dictionary tidak ditemukan. Normalizer berjalan tanpa kamus.")

    except json.JSONDecodeError as e:
      logger.error(f"Error parsing JSON slang dictionary: {e}. Normalizer berjalan tanpa kamus.")
      self.dictionary = {}
    except Exception as e:
      logger.error(f"Error membuka slang dictionary: {e}. Normalizer berjalan tanpa kamus.")
      self.dictionary = {}

  def normalize(self, text: str) -> str:
    """Normalisasi teks slang"""
    if not self.dictionary:
      return text.lower()

    words = text.lower().split()
    normalized_words = [self.dictionary.get(word, word) for word in words]
    return " ".join(normalized_words)

  async def close(self):
    """Tutup koneksi Redis"""
    await self.redis_client.close()
    await self.redis_client.connection_pool.disconnect()


# --- Inisialisasi global ---
async def init_slang_normalizer():
  redis_client = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
  dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'dictSlang.json')

  normalizer = SlangNormalizer(dict_path, redis_client)
  await normalizer.load_dictionary()

  return normalizer


# --- Jalankan langsung (opsional) ---
# if __name__ == "__main__":
#   async def main():
#     normalizer = await init_slang_normalizer()
#     sample = "gmn kabar bro?"
#     print("Input:", sample)
#     print("Normalized:", normalizer.normalize(sample))
#     await normalizer.close()

#   asyncio.run(main())
