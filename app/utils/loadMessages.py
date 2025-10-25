import redis
import os
import json
import logging

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MESSAGES_CALLBACK = {} 
dict_path = os.path.join(os.path.dirname(__file__), '..', 'dict', 'dictMessages.json')

def load_messages_callback():
  global MESSAGES_CALLBACK

  cached_json = redis_client.get("messages_dict") 

  if cached_json:
    try:
      MESSAGES_CALLBACK = json.loads(cached_json)
      print(f"✅ Kamus Messages dimuat dari Redis.")
      return 
    except json.JSONDecodeError:
      logger.error("Error decode JSON dari Redis. Memuat dari file...")
      MESSAGES_CALLBACK = {} 

  if not MESSAGES_CALLBACK:
    try:
      with open(dict_path, 'r', encoding='utf-8') as f:
        MESSAGES_CALLBACK = json.load(f) 

      if MESSAGES_CALLBACK:
        redis_client.set("messages_dict", json.dumps(MESSAGES_CALLBACK)) 
        print(f"✅ Kamus Messages disimpan ke Redis.")
      else:
        logger.error("Kamus dictMessages.json kosong atau tidak valid.")

    except FileNotFoundError:
      logger.error("File dictMessages.json tidak ditemukan. Callback messages tidak akan tersedia.")
      MESSAGES_CALLBACK = {}
    except json.JSONDecodeError:
      logger.error("Error: Format JSON di dictMessages.json tidak valid.")
      MESSAGES_CALLBACK = {}
    except Exception as e:
      logger.error(f"Error tidak terduga saat memuat messages: {e}")
      MESSAGES_CALLBACK = {}
            
def get_messages_from_redis():
  messages_dict = {}
  try:
    cached_json = redis_client.get("messages_dict")

    if cached_json:
      messages_dict = json.loads(cached_json)

    return None
  except redis.exceptions.ConnectionError as e:
    logger.error(f"Gagal terhubung ke Redis: {e}")
  except json.JSONDecodeError:
    logger.error("Gagal parse data dari Redis (bukan JSON valid).")
  except Exception as e:
    logger.error(f"Error tidak terduga saat mengambil dari Redis: {e}")
      
  return messages_dict


# init function
load_messages_callback()
