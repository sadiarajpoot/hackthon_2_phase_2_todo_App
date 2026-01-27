# Data Model: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-webapp
**Date**: 2026-01-05

## Entity: User

**Description**: Represents a registered user of the todo application

**Fields**:
- `id` (UUID/String): Unique identifier for the user
- `email` (String): User's email address (unique, required)
- `password_hash` (String): Hashed password (required, encrypted)
- `created_at` (DateTime): Timestamp of account creation
- `updated_at` (DateTime): Timestamp of last update
- `is_active` (Boolean): Account status flag (default: true)

**Validation Rules**:
- Email must follow standard email format
- Email must be unique across all users
- Password must meet minimum security requirements (handled by Better Auth)
- Email cannot be empty

**Relationships**:
- One-to-Many: User has many Tasks

## Entity: Task

**Description**: Represents a todo item belonging to a specific user

**Fields**:
- `id` (UUID/String): Unique identifier for the task
- `title` (String): Task title (required)
- `description` (String): Optional detailed description
- `is_completed` (Boolean): Completion status (default: false)
- `user_id` (UUID/String): Reference to the owning user
- `created_at` (DateTime): Timestamp of task creation
- `updated_at` (DateTime): Timestamp of last update
- `due_date` (DateTime): Optional due date for the task

**Validation Rules**:
- Title cannot be empty
- Title must be between 1-200 characters
- Description must be under 1000 characters if provided
- user_id must reference a valid existing user
- User can only access tasks they own

**Relationships**:
- Many-to-One: Task belongs to one User (via user_id)

## State Transitions

### Task State Transitions
- **Pending → Completed**: When user marks task as complete
- **Completed → Pending**: When user unmarks task as complete

### User State Transitions
- **Inactive → Active**: During successful registration
- **Active → Inactive**: If account is deactivated (future feature)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP
);
```

## Indexes
- Index on users.email for efficient login lookups
- Index on tasks.user_id for efficient user-specific queries
- Index on tasks.created_at for chronological sorting

## Security Considerations
- All user data is isolated by user_id foreign key relationships
- No cross-user data access at database level
- Passwords are stored as secure hashes
- User authentication required before any data access