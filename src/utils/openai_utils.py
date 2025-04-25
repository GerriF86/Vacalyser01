# openai_utils.py

import os
import re
from typing import List, Optional
import openai
import requests
import streamlit as st

from dotenv import load_dotenv

load_dotenv()  # This will read .env file and set environment variables

openai.api_key = os.getenv("OPENAI_API_KEY")

def __init__(self, openai_api_key: Optional[str] = None, local_model: Optional[str] = None, default_openai_model: str = "gpt-3.5-turbo"):
        """
        :param openai_api_key: your OpenAI key (if using OpenAI).
        :param local_model: local HF model path (if using a local model).
        :param default_openai_model: which GPT model to use (e.g., gpt-3.5-turbo).
        """
        self.provider = "openai"
        self.openai_model = default_openai_model
        self._pipeline = None

        if local_model:
            # Use local HF model
            self.provider = "local"
            try:
                from transformers import pipeline
            except ImportError:
                raise ImportError("Please install 'transformers' to use local models.")
            try:
                self._pipeline = pipeline("text-generation", model=local_model, tokenizer=local_model, device_map="auto")
            except Exception as e:
                raise RuntimeError(f"Failed to load local model '{local_model}': {e}")
        else:
            # Use OpenAI
            try:
                import openai
            except ImportError:
                raise ImportError("Please install 'openai' to use OpenAI API.")
            if openai_api_key:
                openai.api_key = openai_api_key
            else:
                env_key = st.secrets["OPENAI_API_KEY"]
                if env_key:
                    openai.api_key = env_key
                else:
                    raise ValueError("No OpenAI API key provided or found in environment.")
            self.provider = "openai"

def openai_completion(self, prompt: str, system_message: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """
        Generate text using either OpenAI ChatCompletion or a local HF pipeline.
        """
        if self.provider == "openai":
            import openai
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            try:
                response = openai.ChatCompletion.create(
                    model=self.openai_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1
                )
                return response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                raise RuntimeError(f"OpenAI API request failed: {e}")
        else:
            # Local HF pipeline
            if not self._pipeline:
                raise RuntimeError("Local pipeline not initialized.")
            full_prompt = (system_message + "\n" + prompt) if system_message else prompt
            try:
                outputs = self._pipeline(full_prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature, num_return_sequences=1)
                generated_text = outputs[0]["generated_text"]
                # Remove prompt from output if present
                if generated_text.startswith(full_prompt):
                    generated_text = generated_text[len(full_prompt):]
                return generated_text.strip()
            except Exception as e:
                raise RuntimeError(f"Local model generation failed: {e}")
