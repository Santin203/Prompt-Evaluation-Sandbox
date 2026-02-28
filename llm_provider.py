"""
LLM Provider Abstraction Layer
Supports: Groq (free), Google Gemini (free), Ollama (local/free)
"""

import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def chat(self, system_prompt: str, user_message: str) -> str:
        """Send a message with a system prompt and return the response text."""
        ...

    @abstractmethod
    def name(self) -> str:
        ...


# ── Groq (Free tier: 14,400 requests/day) ──────────────────────────────────

class GroqProvider(LLMProvider):
    """Uses Groq's free API with Llama / Mixtral / Gemma models."""

    MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]

    def __init__(self, model: str | None = None, api_key: str | None = None):
        from groq import Groq

        self.model = model or self.MODELS[0]
        self._client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))

    def chat(self, system_prompt: str, user_message: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def name(self) -> str:
        return f"Groq ({self.model})"


# ── Google Gemini (Free tier: 15 req/min) ───────────────────────────────────

class GeminiProvider(LLMProvider):
    """Uses Google's free Gemini API."""

    MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    def __init__(self, model: str | None = None, api_key: str | None = None):
        import google.generativeai as genai

        key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=key)
        self.model_name = model or self.MODELS[0]
        self._model = genai.GenerativeModel(self.model_name)

    def chat(self, system_prompt: str, user_message: str) -> str:
        combined = f"System instructions: {system_prompt}\n\nUser query: {user_message}"
        response = self._model.generate_content(combined)
        return response.text

    def name(self) -> str:
        return f"Gemini ({self.model_name})"


# ── Ollama (100% local & free) ──────────────────────────────────────────────

class OllamaProvider(LLMProvider):
    """Uses a locally-running Ollama instance."""

    MODELS = [
        "llama3.2",
        "mistral",
        "gemma2",
        "phi3",
    ]

    def __init__(self, model: str | None = None, host: str | None = None):
        import ollama as _ollama

        self._ollama = _ollama
        self.model = model or self.MODELS[0]
        if host:
            self._client = _ollama.Client(host=host)
        else:
            self._client = _ollama.Client()

    def chat(self, system_prompt: str, user_message: str) -> str:
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response["message"]["content"]

    def name(self) -> str:
        return f"Ollama ({self.model})"


# ── Factory ─────────────────────────────────────────────────────────────────

PROVIDERS = {
    "Groq (Free Cloud)": GroqProvider,
    "Google Gemini (Free Cloud)": GeminiProvider,
    "Ollama (Local)": OllamaProvider,
}


def get_provider(provider_name: str, model: str | None = None, **kwargs) -> LLMProvider:
    """Instantiate a provider by display name."""
    cls = PROVIDERS[provider_name]
    return cls(model=model, **kwargs)
