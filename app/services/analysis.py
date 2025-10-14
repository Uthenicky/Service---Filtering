import re
import json
import os
import redis

from .custom_sentiment import custom_analyzer
from .regex_badwords import contains_badword

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

BADWORDS_SET = set()
dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'dictBadWords.json')


def load_badwords():
    """Load badwords dari Redis jika ada, kalau tidak fallback ke file JSON lalu simpan ke Redis."""
    global BADWORDS_SET
    cached_badwords = redis_client.smembers("badwords")

    if cached_badwords:
      BADWORDS_SET = set(cached_badwords)
      print(f"✅ Kamus badwords dimuat dari Redis dengan {len(BADWORDS_SET)} kata.")
    else:
      try:
        with open(dict_path, 'r', encoding='utf-8') as f:
          words_list = json.load(f)
          BADWORDS_SET = set(words_list["badwords"])
          # print(BADWORDS_SET, "<====")
          # Simpan ke Redis
          if BADWORDS_SET:
            redis_client.delete("badwords")  # clear key lama
            redis_client.sadd("badwords", *BADWORDS_SET)
          print(f"✅ Kamus badwords.json dimuat dari file ({len(BADWORDS_SET)} kata) dan disimpan ke Redis.")
      except FileNotFoundError:
        print("⚠️ File badwords.json tidak ditemukan. Filter kata kasar tidak aktif.")
      except json.JSONDecodeError:
        print("❌ Error: Format JSON tidak valid.")


def normalize_for_profanity_check(word: str) -> str:
  """Membersihkan kata dari variasi umum untuk pengecekan."""
  normalized_word = word.lower()

  leetspeak_map = {
    "4": "a",
    "1": "i",
    "3": "e",
    "0": "o",
    "5": "s",
    "7": "t",
  }
  for k, v in leetspeak_map.items():
    normalized_word = normalized_word.replace(k, v)

  # Hapus non-huruf
  normalized_word = re.sub(r'[^a-z]', '', normalized_word)

  # Compress huruf berulang: "anjiiing" → "anjing"
  normalized_word = re.sub(r'(.)\1+', r'\1', normalized_word)

  return normalized_word


class AnalysisService:
  def analyze_sentiment(self, text: str) -> dict:
    return custom_analyzer.analyze(text)

  def filter_badwords(self, text: str) -> dict:
    """Filter kata kasar menggunakan kamus kustom (Redis + Normalisasi)."""
    words_in_text = text.split()
    found_badwords = set()
    has_badwords = False

    for word in words_in_text:
      normalized_word = normalize_for_profanity_check(word)
      if normalized_word in BADWORDS_SET:
        has_badwords = True
        found_badwords.add(word)
            
    regex_matches = contains_badword(text)
    if regex_matches:
      has_badwords = True
      found_badwords.update(regex_matches)

    censored_text = text
    if has_badwords:
      for word in found_badwords:
        censored_text = censored_text.replace(word, '*' * len(word))

    return {
      "has_badwords": has_badwords,
      "censored_text": censored_text,
      "found_words": list(found_badwords)
    }


# Load badwords saat startup
load_badwords()

analysis_service = AnalysisService()
