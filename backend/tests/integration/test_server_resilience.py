"""
Integration tests for server restart resilience.
Tests that conversation functionality continues to work after simulated server restarts.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import uuid4, UUID
import time
from datetime import datetime


from src.main import app
from src.database import engine
from src.models.conversation import Conversation as ConversationModel
from src.models.message import Message as MessageModel
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService


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


def test_conversation_persistence_across_simulated_restart(client: TestClient, db_session: Session):
    """
    Test that conversation context is preserved after a simulated server restart.

    Scenario: User has an ongoing conversation, server restarts, user continues conversation,
    and context is preserved.
    """
    user_id = str(uuid4())

    # Step 1: Create a conversation with some messages
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Add a second message to establish conversation history
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Add another task to call mom"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("conversation_id") == conversation_id

    # Step 2: Verify conversation and messages are persisted in DB
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    # Fetch the conversation and its messages from the database
    persisted_conversation = conversation_service.get_conversation_by_id_and_user(
        UUID(conversation_id),
        UUID(user_id)
    )
    assert persisted_conversation is not None
    assert str(persisted_conversation.id) == conversation_id

    # Get messages from the conversation
    persisted_messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(persisted_messages) >= 2  # User message + AI response for each interaction

    # Step 3: Simulate server restart by creating new service instances and continuing conversation
    # This verifies that all state is properly persisted in the database and not in memory
    with Session(engine) as new_session:
        new_conversation_service = ConversationService(new_session)
        new_message_service = MessageService(new_session)

        # Verify conversation still exists in new session
        fresh_conversation = new_conversation_service.get_conversation_by_id_and_user(
            UUID(conversation_id),
            UUID(user_id)
        )
        assert fresh_conversation is not None
        assert str(fresh_conversation.id) == conversation_id

        # Continue conversation after simulated restart
        response3 = client.post(
            f"/api/{user_id}/chat",
            json={
                "conversation_id": conversation_id,
                "message": "What tasks do I have?"
            },
            headers={"Authorization": "Bearer fake-jwt-token-1"}
        )

        assert response3.status_code == 200
        data3 = response3.json()
        assert data3.get("conversation_id") == conversation_id

        # Verify the response contains references to the previously created tasks
        response_text = data3.get("response", "").lower()
        assert "grocer" in response_text or "buy" in response_text  # Reference to first task
        assert "mom" in response_text or "call" in response_text    # Reference to second task

    # Step 4: Verify all conversation history is still accessible after "restart"
    final_messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(final_messages) >= 3  # 2 user messages + 2+ AI responses


def test_global_state_independence_after_restart(client: TestClient, db_session: Session):
    """
    Test that global application state doesn't interfere with conversation functionality after restart.

    Scenario: Application variables and caches are reset during restart, but database state remains.
    """
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    # Create conversations for two different users
    # User 1 creates first conversation
    resp1 = client.post(
        f"/api/{user1_id}/chat",
        json={"message": "Add a task for user 1 to buy milk"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )
    assert resp1.status_code == 200
    conv1_data = resp1.json()
    conv1_id = conv1_data.get("conversation_id")
    assert conv1_id is not None

    # User 2 creates second conversation
    resp2 = client.post(
        f"/api/{user2_id}/chat",
        json={"message": "Add a task for user 2 to call doctor"},
        headers={"Authorization": "Bearer fake-jwt-token-2"}
    )
    assert resp2.status_code == 200
    conv2_data = resp2.json()
    conv2_id = conv2_data.get("conversation_id")
    assert conv2_id is not None

    # Verify conversations are different
    assert conv1_id != conv2_id

    # Simulate server restart by verifying data persistence in database
    # Check that user 1's conversation doesn't contain user 2's data
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    user1_conv = conversation_service.get_conversation_by_id_and_user(UUID(conv1_id), UUID(user1_id))
    user2_conv = conversation_service.get_conversation_by_id_and_user(UUID(conv2_id), UUID(user2_id))

    assert user1_conv is not None
    assert user2_conv is not None

    # Verify conversation isolation is maintained
    user1_messages = message_service.get_messages_by_conversation_id(UUID(conv1_id))
    user2_messages = message_service.get_messages_by_conversation_id(UUID(conv2_id))

    # User 1 conversation should have user 1's content
    user1_content = " ".join([msg.content.lower() for msg in user1_messages])
    assert "milk" in user1_content or "buy" in user1_content

    # User 2 conversation should have user 2's content
    user2_content = " ".join([msg.content.lower() for msg in user2_messages])
    assert "doctor" in user2_content or "call" in user2_content

    # Verify no cross-contamination between conversations
    assert "doctor" not in user1_content and "milk" not in user2_content


def test_data_consistency_after_multiple_interactions(client: TestClient, db_session: Session):
    """
    Test that data remains consistent after multiple interactions and simulated restarts.

    Scenario: Long-running conversations maintain data integrity through multiple simulated restarts.
    """
    user_id = str(uuid4())

    # Create a longer conversation sequence
    conversation_id = None
    messages = [
        "Add a task to buy groceries",
        "Add a task to finish report",
        "Add a task to call mom",
        "Show my tasks",
        "Mark task to buy groceries as complete",
        "Show my pending tasks",
        "Update task to finish report to 'finish quarterly report'"
    ]

    responses = []
    for i, message in enumerate(messages):
        if i == 0:
            # First message creates conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={"message": message},
                headers={"Authorization": "Bearer fake-jwt-token-1"}
            )
        else:
            # Continue conversation
            response = client.post(
                f"/api/{user_id}/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": message
                },
                headers={"Authorization": "Bearer fake-jwt-token-1"}
            )

        assert response.status_code == 200
        data = response.json()

        if i == 0:
            conversation_id = data.get("conversation_id")
            assert conversation_id is not None

        responses.append(data)

    # Verify conversation has multiple messages
    message_service = MessageService(db_session)
    all_messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(all_messages) >= len(messages)  # Each user message should have an AI response

    # Simulate multiple "restarts" by verifying database state
    for restart_cycle in range(3):
        # Create fresh service instances to simulate post-restart state
        with Session(engine) as restart_session:
            restart_message_service = MessageService(restart_session)

            # Verify conversation and messages still exist after simulated restart
            restart_messages = restart_message_service.get_messages_by_conversation_id(UUID(conversation_id))
            assert len(restart_messages) == len(all_messages), f"Message count changed after restart cycle {restart_cycle}"

            # Continue conversation after simulated restart
            final_response = client.post(
                f"/api/{user_id}/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": "Show my tasks again"
                },
                headers={"Authorization": "Bearer fake-jwt-token-1"}
            )

            assert final_response.status_code == 200
            final_data = final_response.json()
            assert final_data.get("conversation_id") == conversation_id

            # Verify response still contains relevant task information
            final_response_text = final_data.get("response", "").lower()
            assert "task" in final_response_text or "grocer" in final_response_text

    # Final verification after all simulated restarts
    final_messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(final_messages) >= len(all_messages) + 1  # Previous messages + new response


def test_conversation_timestamp_preservation(client: TestClient, db_session: Session):
    """
    Test that conversation timestamps are properly preserved and updated across simulated restarts.

    Scenario: Conversation updated_at timestamp is maintained properly during server restarts.
    """
    user_id = str(uuid4())

    # Create conversation
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to water plants"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Get initial conversation data
    conversation_service = ConversationService(db_session)
    initial_conversation = conversation_service.get_conversation_by_id_and_user(
        UUID(conversation_id),
        UUID(user_id)
    )
    assert initial_conversation is not None

    initial_updated_at = initial_conversation.updated_at
    time.sleep(0.1)  # Small delay to ensure timestamp difference

    # Add another message
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Add another task to walk the dog"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("conversation_id") == conversation_id

    # Get updated conversation data
    updated_conversation = conversation_service.get_conversation_by_id_and_user(
        UUID(conversation_id),
        UUID(user_id)
    )
    assert updated_conversation is not None

    # Verify timestamp was updated after new message
    assert updated_conversation.updated_at > initial_updated_at

    # Simulate server restart and verify timestamps are preserved
    with Session(engine) as fresh_session:
        fresh_conversation_service = ConversationService(fresh_session)

        # Get conversation from fresh session after simulated restart
        fresh_conversation = fresh_conversation_service.get_conversation_by_id_and_user(
            UUID(conversation_id),
            UUID(user_id)
        )
        assert fresh_conversation is not None

        # Verify the timestamp remains the same as before "restart"
        assert fresh_conversation.updated_at == updated_conversation.updated_at

    # Add final message after simulated restart
    response3 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response3.status_code == 200
    data3 = response3.json()
    assert data3.get("conversation_id") == conversation_id

    # Get final conversation data
    final_conversation = conversation_service.get_conversation_by_id_and_user(
        UUID(conversation_id),
        UUID(user_id)
    )
    assert final_conversation is not None

    # Verify timestamp was updated after final message (after "restart")
    assert final_conversation.updated_at > updated_conversation.updated_at


if __name__ == "__main__":
    pytest.main([__file__])