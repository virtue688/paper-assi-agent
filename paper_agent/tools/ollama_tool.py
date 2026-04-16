from __future__ import annotations

import json
from typing import Any

import requests


class OllamaLLM:
    """Small LLM adapter that keeps services independent of one provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3:3b", timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, **options: Any) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False, "options": options}
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except (requests.RequestException, ValueError, KeyError):
            return self._fallback_generate(prompt)

    def chat(self, messages: list[dict[str, str]], **options: Any) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False, "options": options}
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "").strip()
        except (requests.RequestException, ValueError, KeyError):
            merged = "\n".join(item.get("content", "") for item in messages)
            return self._fallback_generate(merged)

    def summarize_text(self, text: str, max_chars: int = 900) -> str:
        prompt = f"Summarize this academic paper abstract in Chinese with method, contribution, and limitation:\n{text[:4000]}"
        return self.generate(prompt)[:max_chars]

    def json_generate(self, prompt: str, fallback: Any) -> Any:
        raw = self.generate(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end >= start:
                return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass
        return fallback

    def _fallback_generate(self, prompt: str) -> str:
        compact = " ".join(prompt.split())
        if len(compact) > 900:
            compact = compact[:900] + "..."
        return "[LLM fallback] Ollama unavailable; heuristic summary from local text: " + compact
