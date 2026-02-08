# Quickstart Guide: Chat API Endpoint for Todo AI Chatbot

## Overview
This guide provides the essential steps to set up and run the Chat API endpoint that enables AI-powered task management through a conversational interface.

## Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- PostgreSQL (or Neon Serverless PostgreSQL for cloud deployment)
- Existing Phase II backend setup with task models
- OpenAI API key
- MCP tools server running

## Environment Setup

### Backend Configuration
1. Set up environment variables in your `.env` file:
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db

# JWT Configuration (from existing Phase II)
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MCP Tools Configuration
MCP_TOOLS_ENDPOINT=http://localhost:8001  # Or your MCP tools server URL

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CHAT_API_PORT=8000
```

## Running the Chat API Server

### 1. Install Dependencies
```bash
# Navigate to backend directory
cd backend

# Install with poetry (recommended) or pip
poetry install
# OR
pip install -r requirements.txt
```

### 2. Start the Chat API Server
```bash
# Run the chat API server
cd backend
uvicorn src.api.chat:app --reload --port 8000
```

## API Endpoint Usage

### POST /api/{user_id}/chat
Send a message to the AI chatbot and receive a response.

**Request Body**:
```json
{
  "conversation_id": "optional-conversation-id", // Leave out to start new conversation
  "message": "Add a task to buy groceries"
}
```

**Response**:
```json
{
  "conversation_id": "conversation-id",
  "response": "I've created a task 'buy groceries' for you.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"user_id": "user-123", "title": "buy groceries"},
      "result": {"task_id": "task-456", "status": "created", "title": "buy groceries"}
    }
  ]
}
```

## Testing the API

### Using curl
```bash
# Start a new conversation
curl -X POST "http://localhost:8000/api/user-123/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Continue an existing conversation
curl -X POST "http://localhost:8000/api/user-123/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "conversation_id": "conversation-456",
    "message": "Show all my tasks"
  }'
```

## Key Components

### API Layer
- Located in `backend/src/api/chat.py`
- Handles authentication and request validation
- Coordinates with services to process messages

### Service Layer
- Located in `backend/src/services/conversation_service.py` and `message_service.py`
- Implements business logic for conversation and message operations
- Ensures data consistency and validation

### AI Agent Integration
- Located in `backend/src/agents/chat_agent.py`
- Connects to MCP tools for task operations
- Processes natural language into tool calls

### Data Models
- Located in `backend/src/models/conversation.py` and `message.py`
- SQLModel definitions for conversations and messages
- Proper relationships and validation rules

## Testing

### Unit Tests
```bash
# Run chat API unit tests
cd backend
pytest tests/unit/api/test_chat.py
```

### Integration Tests
```bash
# Run chat API integration tests
cd backend
pytest tests/integration/test_chat_api.py
```

## Troubleshooting

### Common Issues
- **Authentication errors**: Verify JWT token is valid and user_id in path matches token
- **Database connection**: Check that DATABASE_URL is correct
- **MCP tools unavailable**: Verify MCP tools server is running and accessible
- **Rate limiting**: Check that you're not exceeding API limits

### Logs
- API logs: Check console output from uvicorn server
- Error logs: Look for specific error messages in the server output
- Conversation logs: Track conversation flow in the logs