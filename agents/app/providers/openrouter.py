"""OpenRouter AI provider with retry logic."""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from openai import AsyncOpenAI

from app.core.models import BaseAIProvider, ProviderConfig
from app.core.helpers import extract_api_key


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter provider using OpenAI-compatible API with retry logic."""
    
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    MAX_RETRIES = 3
    KEY_NAMES = ["openrouter", "api_key", "apiKey", "token"]
    
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
                raise ValueError("OpenRouter API key not found in tokens. Expected one of: " + ", ".join(self.KEY_NAMES))
            
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.OPENROUTER_BASE_URL,
            )
            logger.debug("OpenRouter client created with base URL: {}", self.OPENROUTER_BASE_URL)
            return self._client
    
    async def generate(
        self,
        prompt: str,
        tokens: Dict[str, Any] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate content with retry logic for transient errors."""
        client = await self._get_client(tokens or {})
        
        model = self._config.model
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                if attempt > 0:
                    delay = attempt * 2
                    logger.warning("Retry attempt {} for OpenRouter, waiting {}s...", attempt, delay)
                    await asyncio.sleep(delay)
                
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                if not response.choices or len(response.choices) == 0:
                    raise ValueError("Empty response from OpenRouter")
                
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
                
                logger.info("OpenRouter generation successful: {} tokens used", tokens_used)
                return content
                
            except Exception as e:
                last_error = e
                
                # Check if error is transient (retry) or permanent (fail immediately)
                if self._is_transient_error(e):
                    logger.warning("Transient error on attempt {}: {}", attempt + 1, str(e))
                    continue
                else:
                    # Auth error, rate limit, etc. - don't retry
                    logger.error("Non-transient error: {}", str(e))
                    raise
        
        # All retries exhausted
        logger.error("All {} retries exhausted", self.MAX_RETRIES)
        raise last_error
    
    def _is_transient_error(self, error: Exception) -> bool:
        """Check if error is transient and worth retrying."""
        error_str = str(error).lower()
        transient_keywords = [
            "eof", "connection reset", "timeout", "connection refused",
            "service unavailable", "502", "503", "504", "rate limit"
        ]
        return any(keyword in error_str for keyword in transient_keywords)
    
    def name(self) -> str:
        return "openrouter"
