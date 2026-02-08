"""
Caching utilities for the chat API.
Provides caching for frequently accessed data to improve performance.
"""
from typing import Optional, Dict, Any
import time
from datetime import datetime, timedelta
from uuid import UUID
import json


class SimpleCache:
    """
    Simple in-memory cache for storing frequently accessed data.
    Stores cached items with TTL (time-to-live) expiration.
    """

    def __init__(self, default_ttl_seconds: int = 300):  # 5 minutes default TTL
        self.default_ttl = default_ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Store a value in the cache with optional TTL.

        Args:
            key: Cache key to store the value under
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses default if not provided)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiration_time = time.time() + ttl

        self.cache[key] = {
            "value": value,
            "expiration": expiration_time
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key: Cache key to retrieve value for

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self.cache:
            return None

        item = self.cache[key]
        if time.time() > item["expiration"]:
            # Item has expired, remove it
            del self.cache[key]
            return None

        return item["value"]

    def delete(self, key: str):
        """
        Remove a value from the cache.

        Args:
            key: Cache key to remove
        """
        if key in self.cache:
            del self.cache[key]

    def clear_expired(self):
        """
        Remove all expired items from the cache.
        """
        current_time = time.time()
        expired_keys = [key for key, item in self.cache.items() if current_time > item["expiration"]]

        for key in expired_keys:
            del self.cache[key]

    def clear_all(self):
        """
        Clear all items from the cache.
        """
        self.cache.clear()

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired, False otherwise
        """
        if key not in self.cache:
            return False

        item = self.cache[key]
        if time.time() > item["expiration"]:
            # Item has expired, remove it
            del self.cache[key]
            return False

        return True


# Global cache instances
conversation_cache = SimpleCache(default_ttl_seconds=600)  # 10 minutes for conversations
user_tasks_cache = SimpleCache(default_ttl_seconds=300)   # 5 minutes for user tasks
message_history_cache = SimpleCache(default_ttl_seconds=900)  # 15 minutes for message history


class CacheManager:
    """
    Manager class for handling caching operations with appropriate keys and TTLs.
    """

    def __init__(self):
        self.conversation_cache = conversation_cache
        self.user_tasks_cache = user_tasks_cache
        self.message_history_cache = message_history_cache

    def get_conversation_cache_key(self, conversation_id: UUID) -> str:
        """
        Generate a cache key for a conversation.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Cache key string
        """
        return f"conversation:{conversation_id}"

    def get_user_tasks_cache_key(self, user_id: UUID) -> str:
        """
        Generate a cache key for a user's tasks.

        Args:
            user_id: The ID of the user

        Returns:
            Cache key string
        """
        return f"user_tasks:{user_id}"

    def get_message_history_cache_key(self, conversation_id: UUID) -> str:
        """
        Generate a cache key for message history.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Cache key string
        """
        return f"message_history:{conversation_id}"

    def cache_conversation(self, conversation_id: UUID, conversation_data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        """
        Cache conversation data.

        Args:
            conversation_id: The ID of the conversation
            conversation_data: The conversation data to cache
            ttl_seconds: Optional TTL for the cache entry
        """
        key = self.get_conversation_cache_key(conversation_id)
        self.conversation_cache.set(key, conversation_data, ttl_seconds)

    def get_cached_conversation(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get cached conversation data.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Cached conversation data if found, None otherwise
        """
        key = self.get_conversation_cache_key(conversation_id)
        return self.conversation_cache.get(key)

    def invalidate_conversation_cache(self, conversation_id: UUID):
        """
        Remove a conversation from cache.

        Args:
            conversation_id: The ID of the conversation to invalidate
        """
        key = self.get_conversation_cache_key(conversation_id)
        if self.conversation_cache.has(key):
            self.conversation_cache.delete(key)

    def cache_user_tasks(self, user_id: UUID, tasks: list, ttl_seconds: Optional[int] = None):
        """
        Cache a user's tasks.

        Args:
            user_id: The ID of the user
            tasks: List of tasks to cache
            ttl_seconds: Optional TTL for the cache entry
        """
        key = self.get_user_tasks_cache_key(user_id)
        self.user_tasks_cache.set(key, tasks, ttl_seconds)

    def get_cached_user_tasks(self, user_id: UUID) -> Optional[list]:
        """
        Get cached user tasks.

        Args:
            user_id: The ID of the user

        Returns:
            Cached tasks if found, None otherwise
        """
        key = self.get_user_tasks_cache_key(user_id)
        return self.user_tasks_cache.get(key)

    def invalidate_user_tasks_cache(self, user_id: UUID):
        """
        Remove a user's tasks from cache.

        Args:
            user_id: The ID of the user
        """
        key = self.get_user_tasks_cache_key(user_id)
        if self.user_tasks_cache.has(key):
            self.user_tasks_cache.delete(key)

    def cache_message_history(self, conversation_id: UUID, messages: list, ttl_seconds: Optional[int] = None):
        """
        Cache message history for a conversation.

        Args:
            conversation_id: The ID of the conversation
            messages: List of messages to cache
            ttl_seconds: Optional TTL for the cache entry
        """
        key = self.get_message_history_cache_key(conversation_id)
        self.message_history_cache.set(key, messages, ttl_seconds)

    def get_cached_message_history(self, conversation_id: UUID) -> Optional[list]:
        """
        Get cached message history.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Cached messages if found, None otherwise
        """
        key = self.get_message_history_cache_key(conversation_id)
        return self.message_history_cache.get(key)

    def invalidate_message_history_cache(self, conversation_id: UUID):
        """
        Remove message history from cache.

        Args:
            conversation_id: The ID of the conversation
        """
        key = self.get_message_history_cache_key(conversation_id)
        if self.message_history_cache.has(key):
            self.message_history_cache.delete(key)

    def clear_expired_caches(self):
        """
        Remove all expired items from all caches.
        """
        self.conversation_cache.clear_expired()
        self.user_tasks_cache.clear_expired()
        self.message_history_cache.clear_expired()


# Convenience functions
def cache_user_tasks_data(user_id: UUID, tasks: list):
    """
    Cache a user's tasks for improved performance.

    Args:
        user_id: The ID of the user
        tasks: List of tasks to cache
    """
    cache_manager = CacheManager()
    cache_manager.cache_user_tasks(user_id, tasks)


def get_cached_user_tasks_data(user_id: UUID) -> Optional[list]:
    """
    Get a user's cached tasks.

    Args:
        user_id: The ID of the user

    Returns:
        Cached tasks if found, None otherwise
    """
    cache_manager = CacheManager()
    return cache_manager.get_cached_user_tasks(user_id)


def cache_conversation_data(conversation_id: UUID, conversation_data: Dict[str, Any]):
    """
    Cache conversation data for improved performance.

    Args:
        conversation_id: The ID of the conversation
        conversation_data: The conversation data to cache
    """
    cache_manager = CacheManager()
    cache_manager.cache_conversation(conversation_id, conversation_data)


def get_cached_conversation_data(conversation_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached conversation data.

    Args:
        conversation_id: The ID of the conversation

    Returns:
        Cached conversation data if found, None otherwise
    """
    cache_manager = CacheManager()
    return cache_manager.get_cached_conversation(conversation_id)


def invalidate_user_cache(user_id: UUID):
    """
    Invalidate all cached data for a user.

    Args:
        user_id: The ID of the user
    """
    cache_manager = CacheManager()
    cache_manager.invalidate_user_tasks_cache(user_id)


def invalidate_conversation_cache(conversation_id: UUID):
    """
    Invalidate all cached data for a conversation.

    Args:
        conversation_id: The ID of the conversation
    """
    cache_manager = CacheManager()
    cache_manager.invalidate_conversation_cache(conversation_id)
    cache_manager.invalidate_message_history_cache(conversation_id)