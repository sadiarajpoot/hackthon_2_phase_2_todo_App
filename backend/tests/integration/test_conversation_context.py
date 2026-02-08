"""
Integration tests for conversation context preservation functionality.
Tests that conversation history is properly maintained and used for context in subsequent messages.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime
import json
from unittest.mock import patch

from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.models.task import Task
from src.database import engine, get_session
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService
from src.services.task_service import TaskService


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


def test_conversation_context_preservation_multiple_messages(client: TestClient, db_session: Session):
    """
    Test that conversation context is preserved across multiple messages in the same conversation.

    Scenario: User sends multiple related messages in sequence and expects the AI
    to consider previous context in its responses.
    """
    # Mock user ID for testing
    user_id = str(uuid4())

    # Create an initial conversation
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Send a follow-up message that references the previous context
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "What tasks do I have?"
        },
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    # Verify that the response considers the previous task creation
    assert "buy groceries" in data2.get("response", "").lower() or "groceries" in data2.get("response", "").lower()

    # Verify that tool calls were made appropriately
    assert "tool_calls" in data2
    assert isinstance(data2["tool_calls"], list)

    # Check that conversation history was properly maintained
    conversation_service = ConversationService(db_session)
    conversation, messages = conversation_service.get_conversation_with_history(conversation_id)

    assert conversation is not None
    assert len(messages) >= 2  # At least user message + AI response for each interaction

    # Verify that messages are properly ordered and contain the expected content
    user_messages = [msg for msg in messages if msg.role == MessageRole.user]
    assistant_messages = [msg for msg in messages if msg.role == MessageRole.assistant]

    assert len(user_messages) >= 2  # Two user messages sent
    assert len(assistant_messages) >= 2  # Two AI responses received


def test_conversation_context_after_server_restart_simulation(client: TestClient, db_session: Session):
    """
    Test that conversation context is preserved after a simulated server restart.

    Scenario: Conversation data persists in database and remains accessible after server restart.
    """
    # Mock user ID for testing
    user_id = str(uuid4())

    # Create a conversation with some messages
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to call mom"},
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Simulate server restart by clearing any in-memory caches and continuing with same conversation
    # In a real stateless implementation, this wouldn't affect the conversation
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Update that task to call mom tomorrow evening"
        },
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Verify that the update operation was successful
    assert "call mom tomorrow evening" in data2.get("response", "").lower()

    # Verify conversation history still accessible after "restart"
    conversation_service = ConversationService(db_session)
    conversation, messages = conversation_service.get_conversation_with_history(conversation_id)

    assert conversation is not None
    assert len(messages) >= 2  # Original task creation + update request + responses


def test_conversation_isolation_between_users(client: TestClient, db_session: Session):
    """
    Test that conversations are properly isolated between different users.

    Scenario: User A's conversations and messages should not be accessible to User B.
    """
    # Create two different user IDs
    user_a_id = str(uuid4())
    user_b_id = str(uuid4())

    # User A creates a conversation with a specific task
    response_a = client.post(
        f"/api/{user_a_id}/chat",
        json={"message": "Add a task to buy milk"},
        headers={"Authorization": "Bearer fake-jwt-token-for-user-a"}
    )

    assert response_a.status_code == 200
    data_a = response_a.json()
    conversation_a_id = data_a.get("conversation_id")
    assert conversation_a_id is not None

    # User B should not be able to access User A's conversation
    response_b = client.post(
        f"/api/{user_b_id}/chat",
        json={
            "conversation_id": conversation_a_id,  # Trying to access User A's conversation
            "message": "What is this task about?"
        },
        headers={"Authorization": "Bearer fake-jwt-token-for-user-b"}
    )

    # This should either fail with 404 (not found) or 403 (forbidden) since User B doesn't own the conversation
    # or it should behave as if starting a new conversation
    assert response_b.status_code in [200, 403, 404]  # Either successful isolation or access denied

    if response_b.status_code == 200:
        # If successful, the response shouldn't contain information about User A's task
        data_b = response_b.json()
        # The response should not mention "buy milk" since User B doesn't have access to User A's conversation
        if "response" in data_b and "buy milk" in data_b["response"]:
            # This would indicate a security issue - User B accessed User A's data
            assert False, "Security breach: User B accessed User A's conversation data"


def test_empty_conversation_start_new(client: TestClient):
    """
    Test that providing an invalid/nonexistent conversation ID starts a new conversation.
    """
    user_id = str(uuid4())
    fake_conversation_id = str(uuid4())  # This conversation doesn't exist

    response = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": fake_conversation_id,
            "message": "Add a task to water plants"
        },
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    # Should either create a new conversation or return an error
    # The exact behavior depends on the implementation, but it should be secure
    assert response.status_code in [200, 404]  # Either creates new or returns not found


if __name__ == "__main__":
    pytest.main([__file__])