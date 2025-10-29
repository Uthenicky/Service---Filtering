import json
import os
import redis
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomSentimentAnalyzer:
  def __init__(self, redis_client: redis.Redis, redis_key: str = "sentiment:global:dict"):
    self.negations = ["tidak", "bukan", "ga", "gak", "kurang"]
    self.redis_client = redis_client
    self.redis_key = redis_key
    self.dictionary = {}

  async def load_dictionary(self):
    """Muat kamus sentimen dari Redis (jika ada), fallback ke file lokal."""
    try:
      # Coba baca Redis di thread terpisah agar tidak blocking
      cached_dict = await asyncio.to_thread(self.redis_client.get, self.redis_key)

      if cached_dict:
        self.dictionary = json.loads(cached_dict)
        logger.info(f"✅ Kamus sentimen dimuat dari Redis ({len(self.dictionary)} entri).")
        return

      # Redis kosong → baca dari file lokal
      dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'sentimentDict.json')
      if os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Gabungkan semua kategori jadi satu dictionary
        for category in data.values():
          if isinstance(category, dict):
            self.dictionary.update(category)

        logger.info(f"Kamus sentimen dibaca dari file ({len(self.dictionary)} entri).")

        # Simpan ke Redis (non-blocking)
        await asyncio.to_thread(
          self.redis_client.set,
          self.redis_key,
          json.dumps(self.dictionary)
        )
        logger.info("Kamus sentimen disimpan ke Redis.")
      else:
        logger.warning("File sentimentDict.json tidak ditemukan. Analyzer berjalan tanpa kamus.")

    except json.JSONDecodeError as e:
      logger.error(f"Error parsing JSON sentiment dictionary: {e}. Analyzer berjalan tanpa kamus.")
    except Exception as e:
      logger.error(f"Error membuka sentiment dictionary: {e}. Analyzer berjalan tanpa kamus.")

  def analyze(self, text: str) -> dict:
    """Analisis sentimen dengan handling negasi dasar."""
    words = text.lower().split()
    score = 0
    found_positive = []
    found_negative = []
    is_negated = False

    for word in words:
      clean_word = word.strip(".,!?:;")

      if clean_word in self.negations:
        is_negated = True
        continue

      word_score = self.dictionary.get(clean_word, 0)
      if word_score != 0:
        if is_negated:
          word_score = -word_score
          is_negated = False

        score += word_score
        if word_score > 0:
          found_positive.append(clean_word)
        else:
          found_negative.append(clean_word)
      else:
        is_negated = False

    return {
      "score": score,
      "positive_words": list(set(found_positive)),
      "negative_words": list(set(found_negative)),
    }

  async def close(self):
    """Dummy close — hanya placeholder biar konsisten dengan class async lain."""
    pass


# --- Inisialisasi global ---
async def init_custom_analyzer():
  redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
  analyzer = CustomSentimentAnalyzer(redis_client)
  await analyzer.load_dictionary()
  return analyzer


# --- Jalankan langsung (opsional) ---
# if __name__ == "__main__":
#   async def main():
#     analyzer = await init_custom_analyzer()
#     sample = "saya tidak suka pelayanan ini tapi makanannya enak"
#     result = analyzer.analyze(sample)
#     print(result)
#     await analyzer.close()

#   asyncio.run(main())
