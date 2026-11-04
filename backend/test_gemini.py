import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
request_timeout = 15

if not api_key:
    print("GEMINI_API_KEY belum diatur di backend/.env")
    sys.exit(1)

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=20_000),
)

print(f"Menguji koneksi ke Gemini API dengan model {model}...")

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model=model,
            contents="Halo, Gemini! Tolong balas dengan 'Halo, dunia!'",
        )
        print(response.text or "Gemini merespons tanpa teks.")
        sys.exit(0)
    except Exception as error:
        print(f"Percobaan {attempt + 1} gagal: {error}")
        if attempt < 2:
            time.sleep(2 * (attempt + 1))

print("Gemini belum berhasil setelah 3 percobaan.")
sys.exit(1)
