# API Contract: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-webapp
**Date**: 2026-01-05
**Version**: 1.0.0

## Authentication API

### POST /api/auth/register
Register a new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created)**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-05T10:00:00Z"
}
```

**Response (400 Bad Request)**:
- Email already exists
- Invalid email format
- Password too weak

### POST /api/auth/login
Authenticate user and return JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com"
  }
}
```

**Response (401 Unauthorized)**:
- Invalid credentials

### POST /api/auth/logout
Logout user (invalidate token)

**Headers**:
```
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

## Tasks API

All task endpoints require authentication unless specified otherwise.

### GET /api/tasks
Get all tasks for the authenticated user

**Headers**:
```
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Sample task",
      "description": "Task description",
      "is_completed": false,
      "user_id": "user-uuid",
      "created_at": "2026-01-05T10:00:00Z",
      "updated_at": "2026-01-05T10:00:00Z",
      "due_date": "2026-01-10T10:00:00Z"
    }
  ]
}
```

### POST /api/tasks
Create a new task for the authenticated user

**Headers**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "title": "New task",
  "description": "Task description (optional)",
  "due_date": "2026-01-10T10:00:00Z"
}
```

**Response (201 Created)**:
```json
{
  "id": "uuid-string",
  "title": "New task",
  "description": "Task description (optional)",
  "is_completed": false,
  "user_id": "user-uuid",
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T10:00:00Z",
  "due_date": "2026-01-10T10:00:00Z"
}
```

### GET /api/tasks/{task_id}
Get a specific task by ID

**Headers**:
```
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "id": "uuid-string",
  "title": "Sample task",
  "description": "Task description",
  "is_completed": false,
  "user_id": "user-uuid",
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T10:00:00Z",
  "due_date": "2026-01-10T10:00:00Z"
}
```

**Response (404 Not Found)**:
- Task does not exist or belongs to another user

### PUT /api/tasks/{task_id}
Update a specific task

**Headers**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true,
  "due_date": "2026-01-10T10:00:00Z"
}
```

**Response (200 OK)**:
```json
{
  "id": "uuid-string",
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true,
  "user_id": "user-uuid",
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T11:00:00Z",
  "due_date": "2026-01-10T10:00:00Z"
}
```

### PATCH /api/tasks/{task_id}/toggle
Toggle completion status of a task

**Headers**:
```
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "id": "uuid-string",
  "title": "Sample task",
  "is_completed": true,
  "updated_at": "2026-01-05T11:00:00Z"
}
```

### DELETE /api/tasks/{task_id}
Delete a specific task

**Headers**:
```
Authorization: Bearer {token}
```

**Response (204 No Content)**:
- Task successfully deleted

**Response (404 Not Found)**:
- Task does not exist or belongs to another user

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details (optional)"
  }
}
```

## Common Error Codes

- `UNAUTHORIZED`: Missing or invalid authentication token
- `FORBIDDEN`: User does not have permission for this resource
- `NOT_FOUND`: Requested resource does not exist
- `VALIDATION_ERROR`: Request data does not meet validation requirements
- `INTERNAL_ERROR`: Server-side error occurred