# Quickstart Guide: MCP Tools for AI Chatbot

## Overview
This guide provides the essential steps to set up and run the MCP (Model Context Protocol) tools server that enables AI agents to manage user tasks.

## Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- PostgreSQL (or Neon Serverless PostgreSQL for cloud deployment)
- Existing Phase II backend setup with task models

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

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MCP_SERVER_PORT=8001
```

## Running the MCP Tools Server

### 1. Install Dependencies
```bash
# Navigate to backend directory
cd backend

# Install with poetry (recommended) or pip
poetry install
# OR
pip install -r requirements.txt
```

### 2. Start the MCP Server
```bash
# Run the MCP server
cd backend
python -m src.mcp.server
```

## MCP Tools Available

### add_task
- **Purpose**: Create a new task for a user
- **Parameters**: user_id (required), title (required), description (optional)
- **Returns**: task_id, status, title

### list_tasks
- **Purpose**: Retrieve user's tasks with optional status filtering
- **Parameters**: user_id (required), status (optional: all, pending, completed)
- **Returns**: Array of task objects

### complete_task
- **Purpose**: Mark a task as completed
- **Parameters**: user_id (required), task_id (required)
- **Returns**: task_id, status, title

### delete_task
- **Purpose**: Delete a task
- **Parameters**: user_id (required), task_id (required)
- **Returns**: task_id, status, title

### update_task
- **Purpose**: Update task title or description
- **Parameters**: user_id (required), task_id (required), title/description (optional)
- **Returns**: task_id, status, title

## Integration with AI Agents

### Connecting an AI Agent
To connect an AI agent to the MCP tools server:
1. Configure the agent to connect to the MCP server endpoint
2. Define the tool schemas based on the MCP protocol
3. Map natural language intents to the appropriate tool calls

### Example Tool Call
```json
{
  "type": "tool-call",
  "name": "add_task",
  "arguments": {
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }
}
```

## Testing

### Unit Tests
```bash
# Run MCP tools unit tests
cd backend
pytest tests/unit/mcp/
```

### Integration Tests
```bash
# Run MCP tools integration tests
cd backend
pytest tests/integration/mcp/
```

## Key Components

### MCP Server
- Located in `backend/src/mcp/server.py`
- Implements the MCP protocol
- Handles tool registration and execution

### Tool Handlers
- Located in `backend/src/mcp/tools/`
- Individual handlers for each tool (add_task, list_tasks, etc.)
- Validate inputs and execute operations via services

### Tool Executor
- Located in `backend/src/mcp/services/tool_executor.py`
- Orchestrates tool execution
- Handles authentication and authorization
- Interfaces with existing task services

## Troubleshooting

### Common Issues
- **Authentication errors**: Ensure user_id in tool calls matches authenticated user
- **Database connection**: Verify DATABASE_URL is correct
- **MCP protocol errors**: Check that tool schemas match expected format

### Logs
- Server logs: Check console output from MCP server
- Error logs: Look for specific error messages in the server output