"""gRPC server implementation for Agents service."""

import asyncio
from concurrent import futures
from typing import Dict, Any

import grpc
from loguru import logger

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.proto import agents_pb2
from app.proto import agents_pb2_grpc
from app.core.agent_service import AgentService
from app.core.models import AgentRequest, AgentResponse


class AgentsGRPCServicer(agents_pb2_grpc.AgentServiceServicer):
    """gRPC servicer for AgentService."""

    def __init__(self, agent_service: AgentService):
        self._agent_service = agent_service

    async def Generate(
        self,
        request: agents_pb2.GenerateRequest,
        context,
    ) -> agents_pb2.GenerateResponse:
        """Handle Generate RPC call."""
        try:
            # Convert gRPC request to internal format
            internal_request = AgentRequest(
                provider=request.provider,
                model=request.model,
                prompt=request.prompt,
                tokens=dict(request.tokens),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            # Call agent service
            response = await self._agent_service.generate(internal_request)
            
            # Convert internal response to gRPC response
            return agents_pb2.GenerateResponse(
                provider=response.provider,
                model=response.model,
                content=response.content,
                tokens_used=response.tokens_used,
                error=response.error or "",
                error_code=response.error_code or "",
            )
            
        except Exception as e:
            logger.error("❌ gRPC Generate error: {}", str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return agents_pb2.GenerateResponse(
                provider=request.provider,
                model=request.model,
                error=str(e),
                error_code="INTERNAL_ERROR",
            )
    
    async def GenerateStream(
        self,
        request: agents_pb2.GenerateRequest,
        context: grpc.ServicerContext,
    ):
        """Handle GenerateStream RPC call (streaming response)."""
        try:
            # For streaming, we'll simulate by calling Generate and sending chunks
            # In a real implementation, this would use streaming APIs from providers
            
            internal_request = AgentRequest(
                provider=request.provider,
                model=request.model,
                prompt=request.prompt,
                tokens=dict(request.tokens),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            # Call generate
            response = await self._agent_service.generate(internal_request)
            
            if response.error:
                yield agents_pb2.GenerateStreamChunk(
                    content="",
                    done=False,
                    error=response.error,
                    tokens_used=0,
                )
                return
            
            # Split content into chunks (simulate streaming)
            # In production, providers would stream directly
            chunk_size = 100
            content = response.content
            
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield agents_pb2.GenerateStreamChunk(
                    content=chunk,
                    done=False,
                    error="",
                    tokens_used=0,
                )
                # Small delay to simulate streaming
                await asyncio.sleep(0.01)
            
            # Send final chunk with done=True
            yield agents_pb2.GenerateStreamChunk(
                content="",
                done=True,
                error="",
                tokens_used=response.tokens_used,
            )
            
        except Exception as e:
            logger.error("❌ gRPC GenerateStream error: {}", str(e))
            yield agents_pb2.GenerateStreamChunk(
                content="",
                done=True,
                error=str(e),
                tokens_used=0,
            )


class GRPCServer:
    """gRPC server wrapper."""
    
    def __init__(self, agent_service: AgentService):
        self._agent_service = agent_service
        self._server = None
    
    async def start(self, port: int = 50053):
        """Start the gRPC server."""
        self._server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
            ]
        )
        
        servicer = AgentsGRPCServicer(self._agent_service)
        agents_pb2_grpc.add_AgentServiceServicer_to_server(servicer, self._server)
        
        address = f'[::]:{port}'
        self._server.add_insecure_port(address)
        
        logger.info("✅ Agents gRPC server starting on port {}", port)
        await self._server.start()
        logger.info("✅ Agents gRPC server is running on {}", address)
        
        try:
            await self._server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Shutting down gRPC server...")
            await self._server.stop(grace=5)
    
    async def stop(self, grace: int = 5):
        """Stop the gRPC server."""
        if self._server:
            await self._server.stop(grace=grace)
            logger.info("gRPC server stopped")
