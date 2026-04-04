"""Data models for the Agents service."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import asyncio


class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    model: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key (can be provided per-request)")
    max_tokens: int = Field(4096, description="Max tokens in response")
    temperature: float = Field(0.7, description="Creativity temperature")
    
    class Config:
        extra = "allow"


class AgentRequest(BaseModel):
    """Request to generate content."""
    provider: str = Field(..., description="Provider name: openrouter, gemini, openai, claude, deepseek, grok")
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="The prompt text")
    tokens: Dict[str, str] = Field(default_factory=dict, description="Auth tokens per-request")
    max_tokens: int = Field(4096, description="Max tokens in response")
    temperature: float = Field(0.7, description="Creativity temperature")


class AgentResponse(BaseModel):
    """Response from AI generation."""
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    content: str = Field("", description="Generated content")
    tokens_used: int = Field(0, description="Tokens used")
    error: Optional[str] = Field(None, description="Error message if any")
    error_code: Optional[str] = Field(None, description="Error code")


class BaseAIProvider(ABC):
    """Abstract base class for all AI providers."""
    
    def __init__(self, config: ProviderConfig):
        self._config = config
        self._client = None
        self._lock = asyncio.Lock()
    
    @property
    def config(self) -> ProviderConfig:
        return self._config
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        tokens: Dict[str, Any] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate content from prompt."""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return provider name."""
        pass
    
    def is_configured(self) -> bool:
        """Check if provider is configured (always True for per-request tokens)."""
        return True
    
    async def _get_client(self, tokens: Dict[str, Any]):
        """Lazy client creation - to be implemented by subclasses."""
        raise NotImplementedError()
