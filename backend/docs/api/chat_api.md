# Chat API Documentation

## Overview
The Chat API provides an endpoint for users to interact with the AI chatbot that can manage their tasks using natural language commands. The API is designed to be stateless with all conversation history persisted to the database.

## Authentication
All endpoints require JWT authentication in the Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

## Endpoints

### POST /api/{user_id}/chat

Process a user's message with the AI chatbot and return an intelligent response.

#### Path Parameters
- `user_id` (string, required): The ID of the user sending the message. Must match the authenticated user.

#### Request Body
```json
{
  "conversation_id": "string", // Optional - UUID of existing conversation, if null creates new
  "message": "string"          // Required - The user's message/command in natural language
}
```

#### Request Examples
```json
// Starting a new conversation
{
  "message": "Add a task to buy groceries"
}

// Continuing an existing conversation
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Show my tasks"
}
```

#### Response
```json
{
  "conversation_id": "string",    // The ID of the conversation (newly created or existing)
  "response": "string",           // The AI's response to the user
  "tool_calls": [                 // Array of MCP tool calls made during processing
    {
      "name": "string",           // Name of the tool called (add_task, list_tasks, etc.)
      "arguments": {              // Arguments passed to the tool
        "user_id": "string",
        "title": "string",
        // ... other arguments
      },
      "result": {                 // Result from the tool call
        "task_id": "string",
        "status": "string",
        "title": "string"
        // ... other result fields
      }
    }
  ]
}
```

#### Response Examples
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I've created a task for you: 'buy groceries' (ID: 456e7890-f12b-34c5-d678-901234567890).",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {
        "user_id": "abc123...",
        "title": "buy groceries"
      },
      "result": {
        "task_id": "456e7890-f12b-34c5-d678-901234567890",
        "status": "created",
        "title": "buy groceries"
      }
    }
  ]
}
```

#### Status Codes
- `200`: Success - AI response returned
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Invalid or missing authentication
- `403`: Forbidden - User ID in path doesn't match authenticated user
- `404`: Not Found - Conversation doesn't exist or doesn't belong to user
- `500`: Internal Server Error - Processing error

### GET /api/{user_id}/conversations

Retrieve all conversations for a user.

#### Path Parameters
- `user_id` (string, required): The ID of the user whose conversations to retrieve. Must match the authenticated user.

#### Query Parameters
- `limit` (integer, optional): Maximum number of conversations to return (default: 20, max: 100)
- `offset` (integer, optional): Number of conversations to skip (default: 0)

#### Response
```json
{
  "conversations": [
    {
      "id": "string",             // Conversation ID
      "title": "string",          // Optional conversation title
      "created_at": "string",     // ISO timestamp when conversation was created
      "updated_at": "string"      // ISO timestamp when conversation was last updated
    }
  ],
  "total_count": 0              // Total number of conversations for the user
}
```

### GET /api/{user_id}/conversations/{conversation_id}

Retrieve a specific conversation with all its messages.

#### Path Parameters
- `user_id` (string, required): The ID of the user who owns the conversation. Must match the authenticated user.
- `conversation_id` (string, required): The ID of the conversation to retrieve.

#### Response
```json
{
  "conversation": {
    "id": "string",
    "title": "string",
    "created_at": "string",
    "updated_at": "string"
  },
  "messages": [
    {
      "id": "string",             // Message ID
      "role": "string",           // Message role: "user", "assistant", or "system"
      "content": "string",        // Message content
      "timestamp": "string",      // ISO timestamp when message was created
      "sequence_number": 0        // Order of message in conversation
    }
  ]
}
```

## MCP Tool Integration

The Chat API integrates with MCP (Model Context Protocol) tools to enable natural language task management:

### Available Tools

1. **add_task**
   - Purpose: Create a new task
   - Parameters: user_id (string), title (string), description (string, optional)
   - Returns: task_id, status, title

2. **list_tasks**
   - Purpose: Retrieve user's tasks with optional status filtering
   - Parameters: user_id (string), status (string, optional: "all", "pending", "completed")
   - Returns: array of task objects

3. **complete_task**
   - Purpose: Mark a task as completed
   - Parameters: user_id (string), task_id (string)
   - Returns: task_id, status, title

4. **delete_task**
   - Purpose: Delete a task
   - Parameters: user_id (string), task_id (string)
   - Returns: task_id, status, title

5. **update_task**
   - Purpose: Update task title or description
   - Parameters: user_id (string), task_id (string), title (string, optional), description (string, optional)
   - Returns: task_id, status, title

## Error Handling

The API returns appropriate error messages for different failure scenarios:

- **Authentication/Authorization**: Error messages indicate authentication or permission issues
- **Validation**: Clear error messages explain what validation failed
- **Tool Execution**: Friendly error messages explain why tool calls failed
- **Database**: Server errors with appropriate status codes

## Security

- User data is isolated by user_id in all operations
- JWT tokens are validated for all requests
- All inputs are sanitized and validated
- Conversation access is restricted to the owning user

## Performance

- Responses typically returned within 3 seconds
- Database queries are optimized with proper indexing
- Conversation history is efficiently loaded and stored
- Rate limiting prevents abuse of the API