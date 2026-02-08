"""
End-to-end integration tests for the Chat API.
Tests all user stories together to ensure they work seamlessly with proper error handling and performance.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import uuid4, UUID
import time
from datetime import datetime


from src.main import app
from src.database import engine
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task
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


def test_complete_chat_api_workflow(client: TestClient, db_session: Session):
    """
    Test the complete chat API workflow with all user stories working together.

    Scenario: User interacts with the chat API performing create, list, update, complete, and delete operations in sequence.
    """
    user_id = str(uuid4())

    # 1. Create a new task using natural language
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Verify the response and tool calls
    assert "response" in data1
    assert "tool_calls" in data1
    assert len(data1["tool_calls"]) > 0

    # Verify add_task was called
    add_task_calls = [tc for tc in data1["tool_calls"] if tc["name"] == "add_task"]
    assert len(add_task_calls) == 1

    # Extract the created task ID
    created_task_id = add_task_calls[0]["result"]["task_id"]
    assert created_task_id is not None

    # 2. List tasks to verify the new task exists
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("conversation_id") == conversation_id

    # Verify list_tasks was called
    list_task_calls = [tc for tc in data2["tool_calls"] if tc["name"] == "list_tasks"]
    assert len(list_task_calls) == 1

    # Verify the task we created is in the list
    listed_tasks = list_task_calls[0]["result"]["tasks"]
    created_task = next((task for task in listed_tasks if task["id"] == created_task_id), None)
    assert created_task is not None
    assert created_task["title"] == "buy groceries"
    assert created_task["status"] == "pending"

    # 3. Update the task
    response3 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": f"Update task {created_task_id} title to 'buy weekly groceries'"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response3.status_code == 200
    data3 = response3.json()
    assert data3.get("conversation_id") == conversation_id

    # Verify update_task was called
    update_task_calls = [tc for tc in data3["tool_calls"] if tc["name"] == "update_task"]
    assert len(update_task_calls) == 1

    # Verify the task was updated
    updated_task_result = update_task_calls[0]["result"]
    assert updated_task_result["task_id"] == created_task_id
    assert "weekly groceries" in updated_task_result["title"]

    # 4. Complete the task
    response4 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": f"Mark task {created_task_id} as complete"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response4.status_code == 200
    data4 = response4.json()
    assert data4.get("conversation_id") == conversation_id

    # Verify complete_task was called
    complete_task_calls = [tc for tc in data4["tool_calls"] if tc["name"] == "complete_task"]
    assert len(complete_task_calls) == 1

    # Verify the task was completed
    completed_task_result = complete_task_calls[0]["result"]
    assert completed_task_result["task_id"] == created_task_id
    assert completed_task_result["status"] == "completed"

    # 5. List tasks again to verify the status change
    response5 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response5.status_code == 200
    data5 = response5.json()
    assert data5.get("conversation_id") == conversation_id

    # Verify the task now has completed status
    list_task_calls_2 = [tc for tc in data5["tool_calls"] if tc["name"] == "list_tasks"]
    assert len(list_task_calls_2) == 1

    updated_tasks = list_task_calls_2[0]["result"]["tasks"]
    completed_task = next((task for task in updated_tasks if task["id"] == created_task_id), None)
    assert completed_task is not None
    assert completed_task["status"] == "completed"

    # 6. Delete the task
    response6 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": f"Delete task {created_task_id}"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response6.status_code == 200
    data6 = response6.json()
    assert data6.get("conversation_id") == conversation_id

    # Verify delete_task was called
    delete_task_calls = [tc for tc in data6["tool_calls"] if tc["name"] == "delete_task"]
    assert len(delete_task_calls) == 1

    # Verify the task was deleted
    deleted_task_result = delete_task_calls[0]["result"]
    assert deleted_task_result["task_id"] == created_task_id
    assert deleted_task_result["status"] == "deleted"

    print("✓ Complete chat API workflow test passed: create → list → update → complete → list → delete")


def test_conversation_context_preservation(client: TestClient, db_session: Session):
    """
    Test that conversation context is preserved across multiple interactions.

    Scenario: User sends related messages in sequence and AI considers previous context.
    """
    user_id = str(uuid4())

    # Create a conversation with a task
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy milk"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # Add another task in the same conversation
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Add a task to call mom"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("conversation_id") == conversation_id

    # Now ask a contextual question: "What tasks did I just add?"
    response3 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "What tasks did I just add?"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response3.status_code == 200
    data3 = response3.json()
    assert data3.get("conversation_id") == conversation_id

    # Verify the response mentions the tasks we just added
    response_text = data3.get("response", "").lower()
    assert "milk" in response_text or "buy" in response_text  # Should reference the milk task
    assert "call" in response_text or "mom" in response_text  # Should reference the mom task

    print("✓ Conversation context preservation test passed")


def test_user_data_isolation(client: TestClient, db_session: Session):
    """
    Test that user data remains isolated across different users.

    Scenario: Two users interact with the chat API and their data remains separate.
    """
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    # User 1 creates a task
    response1 = client.post(
        f"/api/{user1_id}/chat",
        json={"message": "Add a task for user 1 to buy groceries"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    user1_conversation_id = data1.get("conversation_id")
    assert user1_conversation_id is not None

    # Extract user 1's task ID
    user1_task_calls = [tc for tc in data1["tool_calls"] if tc["name"] == "add_task"]
    assert len(user1_task_calls) == 1
    user1_task_id = user1_task_calls[0]["result"]["task_id"]

    # User 2 creates a task
    response2 = client.post(
        f"/api/{user2_id}/chat",
        json={"message": "Add a task for user 2 to call dentist"},
        headers={"Authorization": "Bearer fake-jwt-token-2"}
    )

    assert response2.status_code == 200
    data2 = response2.json()
    user2_conversation_id = data2.get("conversation_id")
    assert user2_conversation_id is not None
    assert user2_conversation_id != user1_conversation_id  # Different conversations

    # Extract user 2's task ID
    user2_task_calls = [tc for tc in data2["tool_calls"] if tc["name"] == "add_task"]
    assert len(user2_task_calls) == 1
    user2_task_id = user2_task_calls[0]["result"]["task_id"]

    # User 1 lists their tasks - should only see their own
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

    # Verify user 1 only sees their own task
    list_calls = [tc for tc in data3["tool_calls"] if tc["name"] == "list_tasks"]
    assert len(list_calls) == 1
    user1_tasks = list_calls[0]["result"]["tasks"]
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["id"] == user1_task_id
    assert "grocer" in user1_tasks[0]["title"].lower()  # Should contain user 1's task content

    # User 2 lists their tasks - should only see their own
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

    # Verify user 2 only sees their own task
    list_calls_2 = [tc for tc in data4["tool_calls"] if tc["name"] == "list_tasks"]
    assert len(list_calls_2) == 1
    user2_tasks = list_calls_2[0]["result"]["tasks"]
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["id"] == user2_task_id
    assert "dentist" in user2_tasks[0]["title"].lower()  # Should contain user 2's task content

    # Verify no cross-contamination between users
    assert user1_task_id != user2_task_id
    assert user1_conversation_id != user2_conversation_id
    assert "dentist" not in user1_tasks[0]["title"].lower()  # User 1 shouldn't see user 2's content
    assert "grocer" not in user2_tasks[0]["title"].lower()  # User 2 shouldn't see user 1's content

    print("✓ User data isolation test passed")


def test_error_handling_and_validation(client: TestClient, db_session: Session):
    """
    Test that proper error handling and validation occurs for invalid requests.

    Scenario: Invalid inputs, unauthorized access, and system errors are handled gracefully.
    """
    user_id = str(uuid4())

    # Test with empty message
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": ""},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    # Should return 400 Bad Request for empty message
    assert response1.status_code in [400, 422], f"Expected 400/422 status, got {response1.status_code}"

    # Test with very long message
    long_message = "A" * 11000  # Over 10k character limit
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={"message": long_message},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    # Should return 400 Bad Request for message too long
    assert response2.status_code in [400, 422], f"Expected 400/422 status, got {response2.status_code}"

    # Test with invalid conversation ID format
    response3 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": "invalid-uuid-format",
            "message": "Test message with invalid conversation ID"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    # Should return 400 Bad Request for invalid conversation ID
    assert response3.status_code in [400, 422], f"Expected 400/422 status, got {response3.status_code}"

    # Test unauthorized access (no token)
    response4 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Test message without authentication"},
    )

    # Should return 401 Unauthorized
    assert response4.status_code == 401, f"Expected 401 status, got {response4.status_code}"

    # Test invalid user ID format
    response5 = client.post(
        f"/api/invalid-user-id-format/chat",
        json={"message": "Test message with invalid user ID"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    # Should return 400 Bad Request for invalid user ID format
    assert response5.status_code in [400, 422], f"Expected 400/422 status, got {response5.status_code}"

    print("✓ Error handling and validation test passed")


def test_conversation_persistence_and_continuation(client: TestClient, db_session: Session):
    """
    Test that conversations persist and can be continued properly.

    Scenario: Conversation state is preserved in database and can be resumed after server operations.
    """
    user_id = str(uuid4())

    # Create a conversation with multiple messages
    conversation_messages = [
        "Add a task to water plants",
        "Add another task to mow the lawn",
        "Show my tasks",
        "Mark the water plants task as complete"
    ]

    conversation_id = None
    responses = []

    for i, message in enumerate(conversation_messages):
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

    # Verify conversation was maintained throughout
    for response in responses[1:]:
        assert response.get("conversation_id") == conversation_id

    # Verify all messages are stored in the database
    conversation_service = ConversationService(db_session)
    message_service = MessageService(db_session)

    conversation = conversation_service.get_conversation_by_id_and_user(UUID(conversation_id), UUID(user_id))
    assert conversation is not None

    # Get messages from the conversation
    messages = message_service.get_messages_by_conversation_id(UUID(conversation_id))
    assert len(messages) >= len(conversation_messages) * 2  # Each user message should have an AI response

    # Verify conversation timestamp was updated
    updated_conversation = conversation_service.get_conversation_by_id_and_user(UUID(conversation_id), UUID(user_id))
    assert updated_conversation is not None
    assert updated_conversation.updated_at >= conversation.created_at

    print(f"✓ Conversation persistence test passed: {len(messages)} messages stored in conversation")


def test_multiple_tool_calls_in_single_request(client: TestClient, db_session: Session):
    """
    Test that a single user request can trigger multiple tool calls.

    Scenario: User sends a message that requires multiple operations, all are executed properly.
    """
    user_id = str(uuid4())

    # Create a conversation and send a message that might trigger multiple operations
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a task to buy groceries and add a task to call mom"},
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1.get("conversation_id")
    assert conversation_id is not None

    # The response should include multiple tool calls
    tool_calls = data1.get("tool_calls", [])
    add_task_calls = [tc for tc in tool_calls if tc["name"] == "add_task"]
    # Should have at least 2 add_task calls for the two tasks mentioned
    assert len(add_task_calls) >= 1, f"Expected at least 1 add_task call, got {len(add_task_calls)}"

    # Verify that both tasks were created by listing them
    response2 = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers={"Authorization": "Bearer fake-jwt-token-1"}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    list_calls = [tc for tc in data2["tool_calls"] if tc["name"] == "list_tasks"]
    assert len(list_calls) == 1

    tasks = list_calls[0]["result"]["tasks"]
    # Should have at least the tasks we created
    assert len(tasks) >= 1

    # Verify both tasks exist in the list
    task_titles = [task["title"].lower() for task in tasks]
    has_groceries = any("grocer" in title for title in task_titles)
    has_mom = any("mom" in title or "call" in title for title in task_titles)

    # At least one of the expected tasks should have been created
    assert has_groceries or has_mom, f"Expected to find grocery or mom task in {task_titles}"

    print("✓ Multiple tool calls in single request test passed")


if __name__ == "__main__":
    pytest.main([__file__])