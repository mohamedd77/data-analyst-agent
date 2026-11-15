import os
import time

import requests

API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiClient:
    """Thin wrapper over the Gemini generateContent REST endpoint."""

    def __init__(self, model=None, api_key=None, timeout=120, max_retries=4):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.api_key = api_key or os.environ["GEMINI_API_KEY"]
        self.timeout = timeout
        self.max_retries = max_retries

    def generate(self, contents, system, tool_declarations):
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "tools": [{"functionDeclarations": tool_declarations}],
        }
        url = f"{API_ROOT}/{self.model}:generateContent"
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                r = requests.post(
                    url, headers={"x-goog-api-key": self.api_key},
                    json=body, timeout=self.timeout,
                )
            except requests.Timeout as e:
                last_error = e
            else:
                if r.status_code not in (429, 503):
                    r.raise_for_status()
                    candidates = r.json().get("candidates") or []
                    content = candidates[0].get("content") if candidates else None
                    if not content:
                        raise RuntimeError("The model returned no content (possibly blocked).")
                    return content
                last_error = RuntimeError(f"HTTP {r.status_code}")
            if attempt < self.max_retries:
                time.sleep(5 * 2 ** attempt)  # 5s, 10s, 20s, 40s
        raise RuntimeError(f"Gemini request failed after retries: {last_error}")
