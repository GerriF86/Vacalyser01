import os, json, requests, streamlit as st
from typing import Literal, List, Dict, Any

try:
    from openai import OpenAI        # only needed if provider=="openai"
except ImportError:
    OpenAI = None                    # protect local-only deployments


class LLMService:
    """
    Unified wrapper around either a local Ollama instance **or** the OpenAI API.
    Call `generate()` and forget the rest.
    """
    def __init__(
        self,
        provider: Literal["ollama", "openai"],
        ollama_api_url: str = "http://127.0.0.1:11434",
        ollama_model: str = "llama3.2:3b",
        openai_api_key: str | None = None,
        openai_model: str = "gpt-4o",
        openai_org: str | None = None,
    ) -> None:

        self.provider = provider.lower()
        if self.provider not in ("ollama", "openai"):
            raise ValueError("provider must be 'ollama' or 'openai'")

        # --- Ollama specific ---
        self.ollama_api_url = ollama_api_url.rstrip("/")
        self.ollama_model   = ollama_model

        # --- OpenAI specific ---
        self.openai_model   = openai_model
        if self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai-python is not installed.")
            self._client = OpenAI(
                api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
                organization=openai_org or os.getenv("OPENAI_ORGANIZATION")
            )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        **kwargs
    ) -> str:
        if self.provider == "ollama":
            return self._generate_ollama(prompt, max_tokens=max_tokens, **kwargs)
        return self._generate_openai(prompt, max_tokens=max_tokens, **kwargs)

    # --------------------------------------------------------------------- #
    # Private helpers
    # --------------------------------------------------------------------- #
    def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        num_ctx: int = 512,
        stream: bool = False,
    ) -> str:
        url = f"{self.ollama_api_url}/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "num_ctx": num_ctx,
            "num_predict": max_tokens,
            "stream": stream,
        }

        try:
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            # Ollama returns *one* JSON line when stream=False
            data = r.json()
            return data.get("response", "")
        except (requests.RequestException, json.JSONDecodeError) as e:
            st.error(f"Ollama error → {e}")
            return ""

    def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float = 0.7,
    ) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:  # pylint: disable=broad-except
            st.error(f"OpenAI error → {e}")
            return ""
