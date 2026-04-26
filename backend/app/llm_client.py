"""
llm_client.py — Async GROQ API wrapper
"""
import json
import re
import httpx
from .config import GROQ_API_KEY, GROQ_BASE, MAX_TOKENS


class LLMClient:
    """Thin async wrapper around the GROQ text-generation API."""

    def __init__(self, api_key: str = GROQ_API_KEY):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def complete(self, prompt: str, system: str = "", max_tokens: int = MAX_TOKENS) -> str:
        """Call GROQ and return the raw text response."""
        body: dict = {
            "input": prompt,
            "max_output_tokens": max_tokens,
            "temperature": 0.0,
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient(timeout=40.0) as client:
            r = await client.post(GROQ_BASE, headers=self.headers, json=body)
            r.raise_for_status()
            data = r.json()
            output = data.get("output")
            if isinstance(output, list):
                if all(isinstance(item, str) for item in output):
                    return "".join(output)
                if len(output) == 1 and isinstance(output[0], dict):
                    return output[0].get("content", "")
            if isinstance(output, str):
                return output
            return data.get("response", data.get("text", ""))

    async def complete_json(self, prompt: str, system: str = "") -> dict | list:
        """Call GROQ and parse the response as JSON (strips markdown fences)."""
        text = await self.complete(prompt, system)
        return self._parse_json(text)

    @staticmethod
    def _parse_json(text: str) -> dict | list:
        clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
        return json.loads(clean)


# Module-level singleton
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
