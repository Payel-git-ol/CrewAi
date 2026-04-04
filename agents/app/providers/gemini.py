"""Google Gemini AI provider."""

from typing import Dict, Any, Optional
from loguru import logger
from google import genai
from google.genai import types

from app.core.models import BaseAIProvider, ProviderConfig
from app.core.helpers import extract_api_key


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider using official SDK."""
    
    KEY_NAMES = ["gemini", "google", "api_key", "apiKey"]
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = None
    
    async def _get_client(self, tokens: Dict[str, Any]):
        """Lazy client creation with API key from tokens."""
        async with self._lock:
            if self._client is not None:
                return self._client
            
            api_key = extract_api_key(tokens, self.KEY_NAMES)
            if not api_key:
                raise ValueError("Gemini API key not found in tokens. Expected one of: " + ", ".join(self.KEY_NAMES))
            
            self._client = genai.Client(api_key=api_key)
            logger.debug("Gemini client created")
            return self._client
    
    async def generate(
        self,
        prompt: str,
        tokens: Dict[str, Any] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate content using Gemini."""
        client = await self._get_client(tokens or {})
        
        model = self._config.model
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        
        try:
            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = await client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            tokens_used = 0
            if response.usage_metadata:
                tokens_used = response.usage_metadata.total_token_count
            
            logger.info("Gemini generation successful: {} tokens used", tokens_used)
            return response.text
            
        except Exception as e:
            logger.error("Gemini generation error: {}", str(e))
            raise
    
    def name(self) -> str:
        return "gemini"
