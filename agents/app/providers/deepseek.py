"""DeepSeek AI provider."""

from typing import Dict, Any, Optional
from loguru import logger
from openai import AsyncOpenAI

from app.core.models import BaseAIProvider, ProviderConfig
from app.core.helpers import extract_api_key


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek provider using OpenAI-compatible API."""
    
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    KEY_NAMES = ["deepseek", "api_key", "apiKey"]
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client: Optional[AsyncOpenAI] = None
    
    async def _get_client(self, tokens: Dict[str, Any]) -> AsyncOpenAI:
        """Lazy client creation with API key from tokens."""
        async with self._lock:
            if self._client is not None:
                return self._client
            
            api_key = extract_api_key(tokens, self.KEY_NAMES)
            if not api_key:
                raise ValueError("DeepSeek API key not found in tokens. Expected one of: " + ", ".join(self.KEY_NAMES))
            
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.DEEPSEEK_BASE_URL,
            )
            logger.debug("DeepSeek client created with base URL: {}", self.DEEPSEEK_BASE_URL)
            return self._client
    
    async def generate(
        self,
        prompt: str,
        tokens: Dict[str, Any] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate content using DeepSeek."""
        client = await self._get_client(tokens or {})
        
        model = self._config.model
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            if not response.choices or len(response.choices) == 0:
                raise ValueError("Empty response from DeepSeek")
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info("DeepSeek generation successful: {} tokens used", tokens_used)
            return content
            
        except Exception as e:
            logger.error("DeepSeek generation error: {}", str(e))
            raise
    
    def name(self) -> str:
        return "deepseek"
