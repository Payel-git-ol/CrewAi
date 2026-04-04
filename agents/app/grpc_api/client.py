"""gRPC client for Agents service - used by Boss, Manager, Worker services.

Usage in Go services:
    - Copy this file's logic to your service
    - Use gRPC to connect to agents:50053
    - Call Generate RPC with provider, model, prompt, tokens
"""

import grpc
from typing import Dict, Any, AsyncGenerator
from loguru import logger

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.proto import agents_pb2
from app.proto import agents_pb2_grpc


class AgentsClient:
    """Async gRPC client for communicating with Agents service."""
    
    def __init__(self, host: str = "localhost", port: int = 50053):
        self._host = host
        self._port = port
        self._channel = None
        self._stub = None
    
    async def _get_channel(self):
        """Get or create gRPC channel."""
        if self._channel is None or self._channel._closed:
            self._channel = grpc.aio.insecure_channel(
                f'{self._host}:{self._port}',
                options=[
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ]
            )
            self._stub = agents_pb2_grpc.AgentServiceStub(self._channel)
        return self._stub
    
    async def generate(
        self,
        provider: str,
        model: str,
        prompt: str,
        tokens: Dict[str, str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> agents_pb2.GenerateResponse:
        """
        Generate content using Agents service.
        
        Args:
            provider: Provider name (openrouter, gemini, openai, claude, deepseek, grok)
            model: Model name
            prompt: Prompt text
            tokens: API tokens per-request
            max_tokens: Max tokens in response
            temperature: Temperature (0.0-1.0)
            
        Returns:
            GenerateResponse with content or error
        """
        stub = await self._get_channel()
        
        request = agents_pb2.GenerateRequest(
            provider=provider,
            model=model,
            prompt=prompt,
            tokens=tokens or {},
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        try:
            response = await stub.Generate(request)
            
            if response.error:
                logger.error("Agents service error: {} - {}", response.error_code, response.error)
            
            return response
            
        except grpc.RpcError as e:
            logger.error("gRPC error calling Agents service: {} - {}", e.code(), e.details())
            return agents_pb2.GenerateResponse(
                provider=provider,
                model=model,
                content="",
                tokens_used=0,
                error=str(e.details()) if hasattr(e, 'details') else str(e),
                error_code="GRPC_ERROR",
            )
    
    async def generate_stream(
        self,
        provider: str,
        model: str,
        prompt: str,
        tokens: Dict[str, str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncGenerator[agents_pb2.GenerateStreamChunk, None]:
        """
        Generate content with streaming.
        
        Yields:
            GenerateStreamChunk with partial content
        """
        stub = await self._get_channel()
        
        request = agents_pb2.GenerateRequest(
            provider=provider,
            model=model,
            prompt=prompt,
            tokens=tokens or {},
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        try:
            async for chunk in stub.GenerateStream(request):
                yield chunk
                
        except grpc.RpcError as e:
            logger.error("gRPC streaming error: {} - {}", e.code(), e.details())
            yield agents_pb2.GenerateStreamChunk(
                content="",
                done=True,
                error=str(e.details()) if hasattr(e, 'details') else str(e),
                tokens_used=0,
            )
    
    async def close(self):
        """Close the gRPC channel."""
        if self._channel and not self._channel._closed:
            await self._channel.close()
            logger.info("Agents client channel closed")
