import json
import os
import redis

class SlangNormalizer:
  def __init__(self, dict_path: str, redis_client: redis.Redis, redis_key: str = "slang_dict"):
    self.dictionary = {}
    self.redis_client = redis_client
    self.redis_key = redis_key
    self.dict_path = dict_path
    self.load_dictionary()

  def load_dictionary(self):
    try:
      # Cek di Redis dulu
      cached_dict = self.redis_client.get(self.redis_key)
      if cached_dict:
        self.dictionary = json.loads(cached_dict)
        print(f"✅ Kamus slang dimuat dari Redis ({len(self.dictionary)} entri).")
        return

      # Kalau Redis kosong → baca dari file
      if os.path.exists(self.dict_path):
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        print(f"📂 Kamus slang berhasil dibaca dari file ({len(self.dictionary)} entri).")

        # Simpan ke Redis
        self.redis_client.set(self.redis_key, json.dumps(self.dictionary))
        print("☁️ Kamus slang disimpan ke Redis.")
      else:
        print("⚠️ File slang dictionary tidak ditemukan. Normalizer berjalan tanpa kamus.")

    except json.JSONDecodeError as e:
      print(f"❌ Error parsing JSON slang dictionary: {e}. Normalizer berjalan tanpa kamus.")
    except Exception as e:
      print(f"❌ Error membuka slang dictionary: {e}. Normalizer berjalan tanpa kamus.")

  def normalize(self, text: str) -> str:
    words = text.lower().split()
    normalized_words = [self.dictionary.get(word, word) for word in words]
    return " ".join(normalized_words)


redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Path dictionary slang
dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'dictSlang.json')

# Init normalizer
normalizer = SlangNormalizer(dict_path, redis_client)

# Contoh uji
# sample_text = "gw gpp bgt makan disini"
# print("Asli   :", sample_text)
# print("Normal :", normalizer.normalize(sample_text))
