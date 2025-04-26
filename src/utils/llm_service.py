# llm_service.py

import os
from typing import Optional, List, Dict, Any

import streamlit as st

# ---------- OpenAI client (v1+) ----------
from openai import OpenAI                         # ➊ pip install --upgrade openai>=1.0
_openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=_openai_api_key)

# ---------- Local model (HF pipeline / Ollama) ----------
def _load_local_pipeline(model_name: str):
    """Lazy-load Transformers pipeline only if the user asked for a local model."""
    from transformers import pipeline
    return pipeline("text-generation", model=model_name, device_map="auto")


class LLMService:
    """
    Unified wrapper around either OpenAI ChatCompletion **or** a local Hugging-Face/Ollama model.
    """

    def __init__(
        self,
        local_model: Optional[str] = None,                # e.g. "ollama/llama3.2:3b"
        default_openai_model: str = "gpt-3.5-turbo",
    ):
        self.provider: str = "local" if local_model else "openai"
        self.openai_model: str = default_openai_model
        self._pipeline = _load_local_pipeline(local_model) if local_model else None

    # --------------------------------------------------------------------- public API
    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        return (
            self._complete_openai(prompt, system_message, temperature, max_tokens)
            if self.provider == "openai"
            else self._complete_local(prompt, system_message, temperature, max_tokens)
        )

    # --------------------------------------------------------------------- providers
    @staticmethod
    def _complete_openai(
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        messages: List[Dict[str, str]] = (
            [{"role": "system", "content": system_message}] if system_message else []
        ) + [{"role": "user", "content": prompt}]

        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()

    def _complete_local(
        self,
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        if not self._pipeline:
            st.error("Local text-generation pipeline could not be initialised.")
            return ""

        full_prompt = f"{system_message}\n{prompt}" if system_message else prompt
        try:
            out: List[Dict[str, Any]] = self._pipeline(
                full_prompt,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                num_return_sequences=1,
            )
            generated = out[0]["generated_text"]
            return generated[len(full_prompt) :].strip() if generated.startswith(full_prompt) else generated.strip()
        except Exception as exc:
            st.error(f"Local model generation failed: {exc}")
            return ""
