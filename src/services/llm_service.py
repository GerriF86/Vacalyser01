# llm_service.py
 
from openai import OpenAI
import streamlit as st


class LLMService:
    """
    A flexible wrapper for either OpenAI or local HF-based LLM calls.
    """

    def __init__(self, openai_api_key=None, local_model=None, default_openai_model="gpt-3.5-turbo"):
        self.provider = "openai"
        self.openai_model = default_openai_model
        self.client = OpenAI(api_key=openai_api_key)
        self.local_model = local_model
        self.pipeline = None

        if local_model:
            self.provider = "local"
            from transformers import pipeline
            self.pipeline = pipeline(
                "text-generation", model=local_model, device_map="auto"
            )
        else:
            self.init_openai(openai_api_key)

    def init_openai(self, openai_api_key):
        import openai
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            openai.api_key = st.secrets["OPENAI_API_KEY"]

    def init_local_model(self, local_model):
        from transformers import pipeline
        try:
            self._pipeline = pipeline(
                "text-generation",
                model=local_model,
                tokenizer=local_model,
                device_map="auto"
            )
        except Exception as e:
            raise RuntimeError(f"Local model load failed: {e}")

    def complete(self, prompt: str, system_message: str = None, temperature: float = 0.7, max_tokens: int = 200):
        if self.provider == "openai":
            return self._complete_openai(prompt, system_message, temperature, max_tokens)
        else:
            return self._complete_local(prompt, temperature, max_tokens)

    def _complete_openai(self, prompt, system_message, temperature, max_tokens):
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _complete_local(self, prompt, system_message, temperature, max_tokens):
        if not self._pipeline:
            st.error("Local pipeline not initialized.")
            return ""
        final_prompt = system_message + "\n" + prompt if system_message else prompt
        try:
            outputs = self._pipeline(
                final_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                num_return_sequences=1
            )
            text = outputs[0]["generated_text"]
            if text.startswith(final_prompt):
                text = text[len(final_prompt):]
            return text.strip()
        except Exception as e:
            st.error(f"Local model generation failed: {e}")
            return ""
