"""Main entry point for Agents service."""

import os
import sys
import asyncio
from loguru import logger

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv
from app.core.agent_service import AgentService
from app.core.models import ProviderConfig
from app.providers.openrouter import OpenRouterProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.claude import ClaudeProvider
from app.providers.deepseek import DeepSeekProvider
from app.providers.grok import GrokProvider
from app.grpc_api.server import GRPCServer


def setup_logging():
    """Configure loguru logger."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    logger.add(
        "logs/agents_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
    )


async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("🚀 Starting Agents service...")
    
    # Initialize agent service
    agent_service = AgentService()
    
    # Define provider configurations
    providers_config = {
        "openrouter": ProviderConfig(
            model=os.getenv("OPENROUTER_MODEL", "qwen/qwen3.6-plus:free"),
            max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
        ),
        "gemini": ProviderConfig(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
        ),
        "openai": ProviderConfig(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        ),
        "claude": ProviderConfig(
            model=os.getenv("CLAUDE_MODEL", "claude-opus-4-6"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.7")),
        ),
        "deepseek": ProviderConfig(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
        ),
        "grok": ProviderConfig(
            model=os.getenv("GROK_MODEL", "grok-3"),
            max_tokens=int(os.getenv("GROK_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("GROK_TEMPERATURE", "0.7")),
        ),
    }
    
    # Initialize and register all providers
    logger.info("🤖 Initializing AI providers...")
    
    openrouter = OpenRouterProvider(providers_config["openrouter"])
    agent_service.register_provider("openrouter", openrouter)
    
    gemini = GeminiProvider(providers_config["gemini"])
    agent_service.register_provider("gemini", gemini)
    
    openai = OpenAIProvider(providers_config["openai"])
    agent_service.register_provider("openai", openai)
    
    claude = ClaudeProvider(providers_config["claude"])
    agent_service.register_provider("claude", claude)
    
    deepseek = DeepSeekProvider(providers_config["deepseek"])
    agent_service.register_provider("deepseek", deepseek)
    
    grok = GrokProvider(providers_config["grok"])
    agent_service.register_provider("grok", grok)
    
    available = agent_service.get_available_providers()
    logger.info("✅ Available AI providers: {}", available)
    
    # Get port
    port = int(os.getenv("AGENTS_PORT", "50053"))
    
    # Start gRPC server
    grpc_server = GRPCServer(agent_service)
    
    logger.info("🌐 Starting gRPC server on port {}", port)
    
    try:
        await grpc_server.start(port)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Agents service...")
        await grpc_server.stop()
        logger.info("✅ Agents service stopped")


if __name__ == "__main__":
    asyncio.run(main())
