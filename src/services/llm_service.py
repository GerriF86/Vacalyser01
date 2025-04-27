import os
import json
import requests

class LLMService:
    """Service to interact with either OpenAI or a local LLM (via Ollama)."""
    def __init__(self, provider: str = "openai", openai_api_key: str = "", openai_org: str = "", openai_model: str = "gpt-3.5-turbo", 
                 ollama_api_url: str = "http://127.0.0.1:11434", ollama_model: str = "llama2:3b"):
        """
        Initialize the LLM service.
        provider: "openai" or "ollama"
        openai_api_key: API key for OpenAI
        openai_org: OpenAI organization (if required)
        openai_model: model name for OpenAI (e.g., "gpt-4" or "gpt-3.5-turbo")
        ollama_api_url: base URL for Ollama local model API
        ollama_model: model name for local LLM via Ollama
        """
        self.provider = provider
        self.openai_model = openai_model
        self.ollama_url = ollama_api_url
        self.ollama_model = ollama_model
        if provider == "openai":
            try:
                import openai
            except ImportError:
                raise ImportError("OpenAI library not installed.")
            if openai_api_key:
                openai.api_key = openai_api_key
            if openai_org:
                openai.organization = openai_org
            self.openai_model = openai_model
        elif provider == "ollama":
            # For local, ensure requests is available (requests imported above)
            self.ollama_url = ollama_api_url
            self.ollama_model = ollama_model
        else:
            raise ValueError("Unsupported LLM provider. Choose 'openai' or 'ollama'.")

    def complete(self, prompt: str, system_message: str = None, max_tokens: int = 256, temperature: float = 0.7) -> str:
        """
        Generate a completion for the given prompt using the specified LLM provider and model.
        For OpenAI, uses ChatCompletion API. For Ollama (local), uses its HTTP API.
        """
        if self.provider == "openai":
            import openai
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response["choices"][0]["message"]["content"].strip()
        elif self.provider == "ollama":
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "num_ctx": 2048,
                "num_predict": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            try:
                res = requests.post(url, json=payload, timeout=120)
                res.raise_for_status()
            except requests.RequestException as e:
                return f"Error: {e}"
            lines = res.text.strip().splitlines()
            output_text = ""
            for line in lines:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        output_text += data["response"]
                except json.JSONDecodeError:
                    continue
            return output_text.strip()
        else:
            return ""
