"""
Integration tests for conversation resumption after server restart.
Tests that conversation context is preserved in the database and accessible after server restart.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import uuid4, UUID
from datetime import datetime
import json
from unittest.mock import patch


from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.models.task import Task
from src.database import engine
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


def test_conversation_resumption_after_simulated_restart(client: TestClient, db_session: Session):
    """
    Test that conversation context is preserved and accessible after server restart simulation.

    Scenario: User has an ongoing conversation, server restarts, user continues conversation,
    and context is preserved.
    """
    # Mock user ID for testing
    user_id = str(uuid4())

    # Step 1: Create a conversation and add some messages
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Add another message to build context
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Add another task to call mom"
        },
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("conversation_id") == conversation_id  # Same conversation continued

    # Step 2: Simulate server restart by verifying data persists in DB
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    # Retrieve conversation and messages from database directly
    conversation = conversation_service.get_conversation_by_id(UUID(conversation_id))
    assert conversation is not None
    assert conversation.user_id == UUID(user_id)

    messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(messages) >= 2  # At least 2 messages (user's 2 requests + AI responses)

    # Verify conversation timestamp was updated
    original_updated_at = conversation.updated_at

    # Step 3: Simulate server restart by creating a new service instance and continuing conversation
    # This verifies that all state is properly persisted in the database
    with Session(engine) as new_session:
        new_conversation_service = ConversationService(new_session)
        new_message_service = MessageService(new_session)

        # Add another message after "restart" - should continue with preserved context
        response3 = client.post(
            f"/api/{user_id}/chat",
            json={
                "conversation_id": conversation_id,
                "message": "What tasks do I have?"
            },
            headers={"Authorization": "Bearer fake-jwt-token"}
        )

        assert response3.status_code == 200
        data3 = response3.json()
        assert data3.get("conversation_id") == conversation_id  # Same conversation continued

        # Verify the conversation was updated in DB after new message
        updated_conversation = new_conversation_service.get_conversation_by_id(UUID(conversation_id))
        assert updated_conversation is not None
        assert updated_conversation.updated_at > original_updated_at

        # Verify all messages are still accessible
        updated_messages = new_message_service.get_messages_by_conversation_id(UUID(conversation_id))
        assert len(updated_messages) >= 3  # Now should have 3+ messages (2 user requests + 2+ AI responses)

        # Check that the response contains information about both tasks
        response_text = data3.get("response", "")
        assert "buy groceries" in response_text.lower() or "grocer" in response_text.lower()
        assert "call mom" in response_text.lower() or "mom" in response_text.lower()


def test_conversation_history_continuity(client: TestClient, db_session: Session):
    """
    Test that conversation history remains continuous and properly ordered.

    Scenario: Messages are stored in order and retrieved in order to maintain conversation flow.
    """
    user_id = str(uuid4())

    # Create a conversation with multiple exchanges
    conversation_messages = [
        "Add a task to buy milk",
        "Add a task to call doctor",
        "Mark the milk task as complete",
        "Show my tasks"
    ]

    conversation_id = None
    responses = []

    for i, message in enumerate(conversation_messages):
        if i == 0:
            # First message creates conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={"message": message},
                headers={"Authorization": "Bearer fake-jwt-token"}
            )
        else:
            # Subsequent messages continue conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                },
                headers={"Authorization": "Bearer fake-jwt-token"}
            )

        assert response.status_code == 200
        data = response.json()

        if i == 0:
            conversation_id = data.get("conversation_id")
            assert conversation_id is not None

        responses.append(data)

    # Verify conversation was created and maintained
    assert conversation_id is not None

    # Verify conversation history contains all messages in correct order
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    conversation, messages = conversation_service.get_conversation_with_history(UUID(conversation_id))
    assert conversation is not None
    assert len(messages) == len(conversation_messages) * 2  # Each user message should have an AI response

    # Check that messages alternate between user and assistant roles
    user_messages = [m for m in messages if m.role == MessageRole.user]
    assistant_messages = [m for m in messages if m.role == MessageRole.assistant]

    assert len(user_messages) == len(conversation_messages)
    assert len(assistant_messages) >= len(conversation_messages)  # May have multiple responses per request

    # Verify sequence numbers are properly ordered
    sorted_messages = sorted(messages, key=lambda x: x.sequence_number)
    for i, msg in enumerate(sorted_messages):
        assert msg.sequence_number == i  # Sequential numbering starting from 0


def test_conversation_isolation_after_restart(client: TestClient, db_session: Session):
    """
    Test that conversation isolation is maintained after restart simulation.

    Scenario: Different users' conversations remain separate even after server restart.
    """
    # Create two different users
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    # User 1 creates a conversation
    response1 = client.post(
        f"/api/{user1_id}/chat",
        json={"message": "Add a task for user 1 to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    user1_conversation_id = data1.get("conversation_id")
    assert user1_conversation_id is not None

    # User 2 creates a conversation
    response2 = client.post(
        f"/api/{user2_id}/chat",
        json={"message": "Add a task for user 2 to call dentist"},
        headers={"Authorization": "Bearer fake-jwt-token-2"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    user2_conversation_id = data2.get("conversation_id")
    assert user2_conversation_id is not None

    # Verify conversations are different
    assert user1_conversation_id != user2_conversation_id

    # User 1 continues their conversation
    response3 = client.post(
        f"/api/{user1_id}/chat",
        json={
            "conversation_id": user1_conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response3.status_code == 200
    data3 = response3.json()
    assert data3.get("conversation_id") == user1_conversation_id
    # Response should mention user 1's task
    assert "grocer" in data3.get("response", "").lower()

    # User 2 continues their conversation
    response4 = client.post(
        f"/api/{user2_id}/chat",
        json={
            "conversation_id": user2_conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-2"}
    )

    assert response4.status_code == 200
    data4 = response4.json()
    assert data4.get("conversation_id") == user2_conversation_id
    # Response should mention user 2's task, not user 1's
    assert "dentist" in data4.get("response", "").lower()
    assert "grocer" not in data4.get("response", "").lower()  # User 2 shouldn't see user 1's tasks


def test_long_conversation_continuation_after_restart(client: TestClient, db_session: Session):
    """
    Test that long conversations maintain context after restart simulation.

    Scenario: Extended conversation with many messages maintains proper context.
    """
    user_id = str(uuid4())

    # Create a longer conversation sequence
    conversation_flow = [
        ("Add a task to buy groceries", "grocer"),
        ("Add a task to finish report", "report"),
        ("Add a task to call mom", "mom"),
        ("Show all my tasks", "task"),
        ("Mark grocery task as complete", "complete"),
        ("Show pending tasks", "pending"),
        ("Show completed tasks", "completed"),
        ("Update the report task to 'finish quarterly report'", "report")
    ]

    conversation_id = None

    for message, expected_content in conversation_flow:
        if conversation_id is None:
            # First message creates conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={"message": message},
                headers={"Authorization": "Bearer fake-jwt-token"}
            )
        else:
            # Continue conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                },
                headers={"Authorization": "Bearer fake-jwt-token"}
            )

        assert response.status_code == 200
        data = response.json()

        if conversation_id is None:
            conversation_id = data.get("conversation_id")
            assert conversation_id is not None

        # Verify response contains expected content
        response_text = data.get("response", "").lower()
        if expected_content:
            assert expected_content in response_text, f"Expected '{expected_content}' in response: {response_text}"

    # After the full conversation flow, verify history is preserved
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    conversation, messages = conversation_service.get_conversation_with_history(UUID(conversation_id))
    assert conversation is not None
    assert len(messages) >= len(conversation_flow) * 2  # Each exchange should have user and assistant messages

    # Verify the conversation has maintained proper context through the entire flow
    # All three tasks should exist in the conversation history
    message_contents = [m.content.lower() for m in messages if m.role == MessageRole.user]
    assert any("grocer" in content for content in message_contents)
    assert any("report" in content for content in message_contents)
    assert any("mom" in content for content in message_contents)


if __name__ == "__main__":
    pytest.main([__file__])