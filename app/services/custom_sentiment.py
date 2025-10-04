import json
import os
import redis

class CustomSentimentAnalyzer:
  def __init__(self, redis_client: redis.Redis, redis_key: str = "sentiment_dict"):
    self.negations = ["tidak", "bukan", "ga", "gak", "kurang"]
    self.redis_client = redis_client
    self.redis_key = redis_key
    self.dictionary = {}
    self._load_dictionary()

  def _load_dictionary(self):
    """Memuat dan menggabungkan kamus sentimen dari Redis atau file JSON."""
    try:
      # Cek di Redis dulu
      cached_dict = self.redis_client.get(self.redis_key)
      if cached_dict:
        self.dictionary = json.loads(cached_dict)
        print(f"✅ Kamus sentimen dimuat dari Redis ({len(self.dictionary)} entri).")
        return

      # Kalau Redis kosong → baca dari file
      dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'sentimentDict.json')
      if os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as f:
          data = json.load(f)
          for category in data.values():
            self.dictionary.update(category)

        print(f"📂 Kamus sentimen berhasil dibaca dari file ({len(self.dictionary)} entri).")

          # Simpan ke Redis
        self.redis_client.set(self.redis_key, json.dumps(self.dictionary))
        print("☁️ Kamus sentimen disimpan ke Redis.")
      else:
        print("⚠️ File sentimentDict.json tidak ditemukan. Analyzer berjalan tanpa kamus.")

    except json.JSONDecodeError as e:
      print(f"❌ Error parsing JSON sentiment dictionary: {e}. Analyzer berjalan tanpa kamus.")
    except Exception as e:
      print(f"❌ Error membuka sentiment dictionary: {e}. Analyzer berjalan tanpa kamus.")

  def analyze(self, text: str) -> dict:
    """Menganalisis teks dan mengembalikan skor sentimen."""
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
          word_score = -word_score  # Balikkan skor jika ada negasi sebelumnya
          is_negated = False  # Reset flag negasi

        score += word_score
        if word_score > 0:
          found_positive.append(clean_word)
        else:
          found_negative.append(clean_word)
      else:
        is_negated = False  # Reset flag jika kata bukan kata sentimen

    return {
      "score": score,
      "positive_words": list(set(found_positive)),
      "negative_words": list(set(found_negative))
    }


redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

custom_analyzer = CustomSentimentAnalyzer(redis_client)

# Contoh Uji
# sample_text = "makanannya enak sekali tapi pelayanannya lambat"
# print("Hasil Analisis:", custom_analyzer.analyze(sample_text))
