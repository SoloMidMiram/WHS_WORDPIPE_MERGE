import os
from openai import OpenAI
from openai import RateLimitError, APIStatusError, APITimeoutError
from dotenv import load_dotenv

# 1) Load API key from .env or environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assert api_key and api_key.startswith("sk-"), "OPENAI_API_KEY missing or malformed"

# 2) (Optional) Proxy support
# Uncomment one of these lines if you use V2Ray or similar:
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"   # HTTP proxy
# os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:10808"  # SOCKS5 proxy (needs: pip install "httpx[socks]")

# 3) Build client
client = OpenAI(api_key=api_key)

# 4) Try a simple, cheap model call
try:
    r = client.responses.create(model="gpt-4.1-mini", input="Return exactly 'OK'.")
    print("✅ Connection successful.")
    print("Model reply:", r.output_text.strip())
except RateLimitError as e:
    print("❌ API key valid, but insufficient quota or plan exhausted.")
    print(e)
except (APIStatusError, APITimeoutError) as e:
    print("❌ API reachable, but request failed or timed out.")
    print(e)
except Exception as e:
    print("❌ Unexpected error.")
    print(e)
