"""
Rate limiting middleware for the chat API.
Prevents abuse and ensures fair usage of the AI chatbot endpoints.
"""
from fastapi import Request, HTTPException, status
from typing import Dict
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter to prevent API abuse.
    Tracks requests per user and applies limits based on time windows.
    """

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_by_user: Dict[str, deque] = defaultdict(deque)  # user_id -> deque of timestamps
        self.blocked_users: Dict[str, datetime] = {}  # user_id -> until when blocked

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from the given user is allowed based on rate limits.

        Args:
            user_id: The ID of the user making the request

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        minute_window = 60  # 60 seconds
        hour_window = 3600  # 3600 seconds

        # Check if user is temporarily blocked
        if user_id in self.blocked_users:
            if datetime.fromtimestamp(current_time) < self.blocked_users[user_id]:
                return False
            else:
                # Unblock user if block period expired
                del self.blocked_users[user_id]

        # Clean up old requests outside the time windows
        self._cleanup_old_requests(user_id, current_time)

        # Get current request history
        user_requests = self.requests_by_user[user_id]

        # Check minute limit
        minute_requests = [req_time for req_time in user_requests if current_time - req_time < minute_window]
        if len(minute_requests) >= self.requests_per_minute:
            # Temporarily block the user
            self.blocked_users[user_id] = datetime.fromtimestamp(current_time) + timedelta(minutes=5)
            logger.warning(f"User {user_id} exceeded minute rate limit, temporarily blocked")
            return False

        # Check hour limit
        hour_requests = [req_time for req_time in user_requests if current_time - req_time < hour_window]
        if len(hour_requests) >= self.requests_per_hour:
            # Temporarily block the user
            self.blocked_users[user_id] = datetime.fromtimestamp(current_time) + timedelta(hours=1)
            logger.warning(f"User {user_id} exceeded hour rate limit, temporarily blocked")
            return False

        # Add current request to history
        user_requests.append(current_time)

        return True

    def _cleanup_old_requests(self, user_id: str, current_time: float):
        """
        Remove requests older than the time windows from tracking.

        Args:
            user_id: The ID of the user
            current_time: Current timestamp for comparison
        """
        user_requests = self.requests_by_user[user_id]
        hour_window = 3600  # 3600 seconds

        # Remove requests older than 1 hour (longest window)
        cutoff_time = current_time - hour_window
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)


def check_rate_limit_for_user(user_id: str) -> bool:
    """
    Check if the user has exceeded rate limits.

    Args:
        user_id: The ID of the user making the request

    Returns:
        True if request is allowed, raises HTTPException if rate limit exceeded
    """
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down your requests."
        )
    return True


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware function to apply rate limiting to incoming requests.

    Args:
        request: The incoming request
        call_next: The next function in the middleware chain

    Returns:
        Response from the next function in the chain
    """
    # Extract user_id from path or other source
    # For chat API endpoints, user_id is typically in the path like /api/{user_id}/chat
    path_parts = request.url.path.split('/')
    user_id = None

    # Look for user_id in the path (typically after 'api' and before 'chat')
    for i, part in enumerate(path_parts):
        if part == 'api' and i + 2 < len(path_parts) and path_parts[i+2] in ['chat', 'conversations']:
            user_id = path_parts[i+1]
            break

    # If we can't extract user_id from the path, try to get it from other sources
    if not user_id:
        # Check if user_id is in request headers or body
        # This is a fallback and in a real implementation, we'd have more sophisticated user identification
        pass

    # Apply rate limiting if we have a user_id
    if user_id:
        check_rate_limit_for_user(user_id)

    # Continue with the request
    response = await call_next(request)
    return response


class ConversationRateLimiter:
    """
    Rate limiter specifically for conversation-related endpoints.
    May have different limits than general API endpoints.
    """

    def __init__(self, requests_per_minute: int = 30, requests_per_hour: int = 500):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_by_user: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a conversation request from the given user is allowed.

        Args:
            user_id: The ID of the user making the request

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        minute_window = 60
        hour_window = 3600

        # Clean up old requests
        self._cleanup_old_requests(user_id, current_time)

        # Get current request history
        user_requests = self.requests_by_user[user_id]

        # Check limits
        minute_requests = [req_time for req_time in user_requests if current_time - req_time < minute_window]
        if len(minute_requests) >= self.requests_per_minute:
            return False

        hour_requests = [req_time for req_time in user_requests if current_time - req_time < hour_window]
        if len(hour_requests) >= self.requests_per_hour:
            return False

        # Add current request
        user_requests.append(current_time)

        return True

    def _cleanup_old_requests(self, user_id: str, current_time: float):
        """
        Remove requests older than the time windows from tracking.
        """
        user_requests = self.requests_by_user[user_id]
        hour_window = 3600  # 3600 seconds

        # Remove requests older than 1 hour
        cutoff_time = current_time - hour_window
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()


# Global conversation rate limiter instance
conversation_rate_limiter = ConversationRateLimiter(requests_per_minute=30, requests_per_hour=500)


def check_conversation_rate_limit(user_id: str) -> bool:
    """
    Check if the user has exceeded conversation rate limits.

    Args:
        user_id: The ID of the user making the request

    Returns:
        True if request is allowed, raises HTTPException if rate limit exceeded
    """
    if not conversation_rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Conversation rate limit exceeded. Please slow down your chat requests."
        )
    return True