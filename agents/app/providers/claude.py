"""Anthropic Claude provider."""

from typing import Dict, Any, Optional
from loguru import logger
import anthropic

from app.core.models import BaseAIProvider, ProviderConfig
from app.core.helpers import extract_api_key


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider using official SDK."""
    
    KEY_NAMES = ["claude", "anthropic", "api_key", "apiKey"]
    
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
                raise ValueError("Claude API key not found in tokens. Expected one of: " + ", ".join(self.KEY_NAMES))
            
            self._client = anthropic.AsyncAnthropic(api_key=api_key)
            logger.debug("Claude client created")
            return self._client
    
    async def generate(
        self,
        prompt: str,
        tokens: Dict[str, Any] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate content using Claude."""
        client = await self._get_client(tokens or {})
        
        model = self._config.model
        max_tokens = max_tokens or self._config.max_tokens
        temperature = temperature if temperature is not None else self._config.temperature
        
        try:
            message = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            if not message.content:
                raise ValueError("Empty response from Claude")
            
            # Claude returns content as list of ContentBlock objects
            content = " ".join(
                block.text if hasattr(block, 'text') else str(block)
                for block in message.content
            )
            
            tokens_used = 0
            if message.usage:
                tokens_used = (
                    (message.usage.input_tokens or 0) + 
                    (message.usage.output_tokens or 0)
                )
            
            logger.info("Claude generation successful: {} tokens used", tokens_used)
            return content
            
        except Exception as e:
            logger.error("Claude generation error: {}", str(e))
            raise
    
    def name(self) -> str:
        return "claude"
