# Data Model: MCP Tools for AI Chatbot

## Entity Relationships

MCP Tools interact with the existing Task entity from Phase II:
```
[AI Agent] → [MCP Tool] → [Task (user-owned)]
```

## Entity Definitions

### Task (Existing from Phase II)
**Description**: Task entity from Phase II, managed through MCP tools called by AI agents

**Fields** (as defined in Phase II):
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table)
- `title`: String (task title)
- `description`: Text (optional task description)
- `status`: Enum (pending|completed)
- `created_at`: DateTime
- `updated_at`: DateTime
- `due_date`: DateTime (optional)

**Validation rules** (as defined in Phase II):
- `user_id` must reference an existing user
- `title` cannot be empty
- `status` must be one of the allowed values

## MCP Tool Request/Response Models

### AddTaskRequest
**Description**: Request model for add_task MCP tool

**Fields**:
- `user_id`: String (required, user identifier)
- `title`: String (required, task title)
- `description`: String (optional, task description)

**Validation rules**:
- `user_id` must be provided
- `title` must be provided and not empty
- `description` must be under character limit if provided

### AddTaskResponse
**Description**: Response model for add_task MCP tool

**Fields**:
- `task_id`: String (ID of created task)
- `status`: String ("created")
- `title`: String (title of created task)

### ListTasksRequest
**Description**: Request model for list_tasks MCP tool

**Fields**:
- `user_id`: String (required, user identifier)
- `status`: String (optional, filter by status: "all", "pending", "completed")

**Validation rules**:
- `user_id` must be provided
- `status` must be one of allowed values if provided

### ListTasksResponse
**Description**: Response model for list_tasks MCP tool

**Fields**:
- `tasks`: Array of Task objects (matching tasks)

### CompleteTaskRequest
**Description**: Request model for complete_task MCP tool

**Fields**:
- `user_id`: String (required, user identifier)
- `task_id`: String (required, task identifier)

**Validation rules**:
- `user_id` must be provided
- `task_id` must be provided and valid
- Task must exist and belong to user

### CompleteTaskResponse
**Description**: Response model for complete_task MCP tool

**Fields**:
- `task_id`: String (ID of updated task)
- `status`: String ("completed")
- `title`: String (title of updated task)

### DeleteTaskRequest
**Description**: Request model for delete_task MCP tool

**Fields**:
- `user_id`: String (required, user identifier)
- `task_id`: String (required, task identifier)

**Validation rules**:
- `user_id` must be provided
- `task_id` must be provided and valid
- Task must exist and belong to user

### DeleteTaskResponse
**Description**: Response model for delete_task MCP tool

**Fields**:
- `task_id`: String (ID of deleted task)
- `status`: String ("deleted")
- `title`: String (title of deleted task)

### UpdateTaskRequest
**Description**: Request model for update_task MCP tool

**Fields**:
- `user_id`: String (required, user identifier)
- `task_id`: String (required, task identifier)
- `title`: String (optional, new task title)
- `description`: String (optional, new task description)

**Validation rules**:
- `user_id` must be provided
- `task_id` must be provided and valid
- Task must exist and belong to user
- At least one of `title` or `description` must be provided

### UpdateTaskResponse
**Description**: Response model for update_task MCP tool

**Fields**:
- `task_id`: String (ID of updated task)
- `status`: String ("updated")
- `title`: String (updated title of task)

## State Transitions

### Task States
```
PENDING → COMPLETED (via complete_task or update_task operations)
COMPLETED → PENDING (via update_task operations)
```

## Access Patterns

### Read Operations
1. Get tasks by user_id and optional status filter (list_tasks)
2. Get specific task by user_id and task_id (used by other operations)

### Write Operations
1. Create new task by user_id (add_task)
2. Update task status by user_id and task_id (complete_task)
3. Update task details by user_id and task_id (update_task)
4. Delete task by user_id and task_id (delete_task)

## Constraints

### Authorization Constraints
- All operations must verify that the user_id in the request matches the authenticated user
- Users can only access tasks that belong to them
- Task operations must validate ownership before execution

### Data Integrity Constraints
- Task titles must not be empty
- Task IDs must be valid and exist before modification operations
- Status values must be from the allowed set