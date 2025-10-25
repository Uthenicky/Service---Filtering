import random
from typing import Optional, List

def extract_phone_number(raw_number: Optional[str]) -> Optional[str]:
  if isinstance(raw_number, str) and raw_number.endswith("@c.us"):
    # Mengambil string dari awal sampai 5 karakter terakhir
    return raw_number[:-5]
  return raw_number

def dynamic_messages(messages: List[str], customer_name: Optional[str] = "Kak") -> str:
  if not messages:
    return "Terjadi kesalahan internal."

  random_message = random.choice(messages)
  name_to_use = customer_name if customer_name else "Kak"
  return random_message.replace("{customerName}", name_to_use)