"""
src/utils/openai_utils.py
─────────────────────────
Unified helper that hides the difference between

• OpenAI Chat Completions API              (provider="openai")
• A local Hugging-Face text-generation model (provider="local")

Example
-------
from src.utils.openai_utils import LLMClient

llm = LLMClient(provider="openai")           # or "local"
reply = llm.chat(
    prompt="Write a 1-sentence job ad for a Data Scientist.",
    system_message="You are an efficient HR copy-writer.",
)
print(reply)
"""

from __future__ import annotations

import os
from typing import Optional, Sequence, Dict, Any

import streamlit as st

# --------------------------------------------------------------------------- #
# Try to import optional deps only when needed
# --------------------------------------------------------------------------- #
try:
    from openai import OpenAI, Client                           # ≥ 1.0 client
except ImportError:  # pragma: no cover
    OpenAI = None

# --------------------------------------------------------------------------- #
# Main helper
# --------------------------------------------------------------------------- #


class LLMClient:
    """Tiny façade that wraps either OpenAI or a local HF pipeline."""

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        provider: str = "openai",
        *,
        # --- OpenAI specific ------------------------------------------ #
        openai_api_key: Optional[str] = None,
        openai_org: Optional[str] = None,
        openai_model: str = "gpt-4o",
        # --- Local model specific ------------------------------------- #
        local_model: Optional[str] = None,
        hf_device_map: str | Dict[str, Any] = "auto",
    ) -> None:
        """
        Parameters
        ----------
        provider :
            "openai"  → OpenAI Chat Completions API  
            "local"   → Hugging-Face `transformers.pipeline`
        openai_api_key :
            Overrides the OPENAI_API_KEY env var / st.secrets.
        local_model :
            Model id or local path understood by 🤗 transformers.
        """
        self.provider = provider.lower().strip()
        if self.provider not in ("openai", "local"):
            raise ValueError("provider must be 'openai' or 'local'")

        self._client = None          # OpenAI client
        self._pipeline = None        # HF pipeline
        self.model_name = openai_model if self.provider == "openai" else local_model

        if self.provider == "openai":
            if OpenAI is None:  # pragma: no cover
                raise ImportError("pip install openai")
            key = (
                openai_api_key
                or os.getenv("OPENAI_API_KEY")
                or st.secrets.get("OPENAI_API_KEY", "")
            )
            if not key:
                raise RuntimeError("OPENAI_API_KEY is missing.")

            self._client = OpenAI(api_key=key, organization=openai_org)

        else:  # local Hugging-Face model
            if local_model is None:
                raise ValueError("local_model must be given when provider='local'")
            try:
                from transformers import pipeline  # lazy import
            except ImportError as exc:  # pragma: no cover
                raise ImportError("pip install transformers") from exc

            self._pipeline = pipeline(
                "text-generation",
                model=local_model,
                tokenizer=local_model,
                device_map=hf_device_map,
            )

    # ------------------------------------------------------------------ #
    # Chat Completion (main public method)
    # ------------------------------------------------------------------ #
    def chat(
        self,
        prompt: str,
        *,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        """
        Generate a single text answer.

        Returns the plain string (no role / metadata).
        """

        if self.provider == "openai":
            messages: list[dict[str, str]] = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            try:
                resp = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as err:  # pragma: no cover
                raise RuntimeError(f"OpenAI request failed → {err}") from err

            return resp.choices[0].message.content.strip()

        # --- Local model branch -------------------------------------- #
        assert self._pipeline is not None  # type checker happy
        full_prompt = f"{system_message}\n{prompt}" if system_message else prompt
        try:
            out = self._pipeline(
                full_prompt,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                num_return_sequences=1,
            )[0]["generated_text"]
            if out.startswith(full_prompt):
                out = out[len(full_prompt):]
            return out.strip()
        except Exception as err:  # pragma: no cover
            raise RuntimeError(f"Local model generation failed → {err}") from err

    # ------------------------------------------------------------------ #
    # Convenience wrapper for non-chat models (legacy code compatibility)
    # ------------------------------------------------------------------ #
    def openai_completion(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        """Alias kept for old calls that expected `openai_completion()`."""
        return self.chat(prompt, temperature=temperature, max_tokens=max_tokens)


# --------------------------------------------------------------------------- #
# Module-level singleton for quick scripts (optional)
# --------------------------------------------------------------------------- #
_default_client: Optional[LLMClient] = None


def _get_default() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(provider="openai")
    return _default_client


# Legacy functional API – kept so other modules using
# `from openai_utils import openai_completion` don’t crash.
def openai_completion(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> str:
    return _get_default().chat(
        prompt,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
    )
