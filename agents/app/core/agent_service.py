"""AgentService - routes AI requests to the appropriate provider."""

from typing import Dict, List
from loguru import logger

from app.core.models import BaseAIProvider, ProviderConfig, AgentRequest, AgentResponse


class AgentService:
    """Service that manages and routes requests to AI providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
    
    def register_provider(self, name: str, provider: BaseAIProvider):
        """Register an AI provider."""
        self._providers[name] = provider
        logger.info("✅ Registered AI provider: {}", name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available and configured providers."""
        return [
            name for name, provider in self._providers.items()
            if provider.is_configured()
        ]
    
    async def generate(self, request: AgentRequest) -> AgentResponse:
        """
        Generate content using the specified provider.
        
        Args:
            request: AgentRequest with provider, model, prompt, tokens, etc.
            
        Returns:
            AgentResponse with generated content or error
        """
        # Find provider
        provider = self._providers.get(request.provider)
        if not provider:
            error_msg = f"Provider '{request.provider}' not found"
            logger.error(error_msg)
            return AgentResponse(
                provider=request.provider,
                model=request.model,
                error=error_msg,
                error_code="PROVIDER_NOT_FOUND",
            )
        
        # Check if configured
        if not provider.is_configured():
            error_msg = f"Provider '{request.provider}' not configured"
            logger.error(error_msg)
            return AgentResponse(
                provider=request.provider,
                model=request.model,
                error=error_msg,
                error_code="PROVIDER_NOT_CONFIGURED",
            )
        
        try:
            logger.info(
                "🤖 [{}] Generating content with model: {}",
                provider.name(),
                request.model,
            )
            
            # Generate content
            content = await provider.generate(
                prompt=request.prompt,
                tokens=request.tokens,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            return AgentResponse(
                provider=request.provider,
                model=request.model,
                content=content,
                tokens_used=0,  # Will be updated by provider if available
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error("❌ Error generating content: {}", error_msg)
            return AgentResponse(
                provider=request.provider,
                model=request.model,
                error=error_msg,
                error_code="GENERATION_ERROR",
            )
