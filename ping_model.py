import os
import time

import requests

KEY = os.environ["GEMINI_API_KEY"]
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]

for model in MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"role": "user", "parts": [{"text": "Reply with one word: pong"}]}]}
    start = time.perf_counter()
    try:
        r = requests.post(url, headers={"x-goog-api-key": KEY}, json=body, timeout=120)
    except requests.RequestException as e:
        print(model, "-> FAILED after", round(time.perf_counter() - start), "s:", type(e).__name__)
        continue
    secs = round(time.perf_counter() - start, 1)
    if r.status_code == 200:
        parts = r.json()["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
        print(model, "-> OK in", secs, "s:", text.strip()[:60])
    else:
        print(model, "-> ERROR", r.status_code, "in", secs, "s:", r.text[:200].replace("\n", " "))
