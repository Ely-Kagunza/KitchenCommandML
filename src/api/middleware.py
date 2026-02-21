"""
API middleware for authentication, logging, and error handling.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""

    def __init__(self, app, api_keys: list):
        """
        Initialize auth middleware.

        Args:
            app: ASGI application
            api_keys: List of valid API keys
        """
        super().__init__(app)
        self.api_keys = api_keys

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Validate API key from request header.

        Args:
            request: HTTP request
            call_next: Next middleware function

        Returns:
            Response or error
        """
        import os
        
        # Skip auth entirely in debug mode
        if os.getenv('DEBUG', 'False').lower() == 'true':
            return await call_next(request)
        
        # Skip auth for health check and docs
        public_paths = ["/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key or api_key not in self.api_keys:
            logger.warning(f"Unauthorized request from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={'error': 'Unauthorized', 'message': 'Invalid or missing API key'}
            )

        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Log request and response details.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        ) 

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"Duration: {duration:.3f}s"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Timestamp"] = datetime.now().isoformat()

        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Handle exceptions and return formatted error response.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response or error response
        """
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now().isoformat()
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Check rate limit for client IP.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response or rate limit exceeded response
        """
        client_ip = request.client.host
        now = time.time()

        # Clean old entries (older than 1 minute)
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > now - 60 for t in times)
        }

        # Get requests for this IP in last minute
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if t > now - 60
        ]

        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"rate limit: {self.requests_per_minute} requests/minute"
                }
            )

        # Add current request
        self.requests[client_ip].append(now)

        return await call_next(request)