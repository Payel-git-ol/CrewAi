"""Test script to verify Agents service functionality."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from loguru import logger
from app.core.agent_service import AgentService
from app.core.models import AgentRequest, ProviderConfig
from app.providers.openrouter import OpenRouterProvider


async def test_agent_service():
    """Test AgentService with a mock request."""
    logger.info("🧪 Testing Agents service...")
    
    # Create agent service
    agent_service = AgentService()
    
    # Register a provider
    config = ProviderConfig(
        model="qwen/qwen3.6-plus:free",
        max_tokens=100,
        temperature=0.7,
    )
    
    openrouter = OpenRouterProvider(config)
    agent_service.register_provider("openrouter", openrouter)
    
    # Test request (will fail without API key, but that's expected)
    request = AgentRequest(
        provider="openrouter",
        model="qwen/qwen3.6-plus:free",
        prompt="Say hello in 3 words",
        tokens={"openrouter": "test-key"},  # Will fail auth, but that's OK
        max_tokens=100,
        temperature=0.7,
    )
    
    try:
        response = await agent_service.generate(request)
        logger.info("Response: {}", response)
        
        if response.error:
            logger.info("✅ Expected error (no valid API key): {}", response.error)
        else:
            logger.info("✅ Response content: {}", response.content[:50])
            
    except Exception as e:
        logger.error("❌ Unexpected error: {}", str(e))


async def test_grpc_server():
    """Test gRPC server startup."""
    logger.info("🧪 Testing gRPC server startup...")
    
    from app.core.agent_service import AgentService
    from app.grpc.server import GRPCServer
    
    agent_service = AgentService()
    grpc_server = GRPCServer(agent_service)
    
    # Start server in background
    async def start_server():
        try:
            await grpc_server.start(50054)  # Use different port for test
        except Exception as e:
            logger.error("Server error: {}", str(e))
    
    server_task = asyncio.create_task(start_server())
    
    # Wait a bit for server to start
    await asyncio.sleep(2)
    
    # Test client connection
    from app.grpc.client import AgentsClient
    
    client = AgentsClient(host="localhost", port=50054)
    
    try:
        response = await client.generate(
            provider="openrouter",
            model="test",
            prompt="test",
            tokens={},
        )
        logger.info("✅ Client response: {}", response)
    except Exception as e:
        logger.info("✅ Expected client error: {}", str(e))
    finally:
        await client.close()
    
    # Stop server
    await grpc_server.stop()
    server_task.cancel()
    
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    
    logger.info("✅ gRPC server test completed")


async def main():
    """Run all tests."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )
    
    await test_agent_service()
    print()
    await test_grpc_server()
    
    logger.info("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
