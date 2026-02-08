# Data Model: Chat API Endpoint for Todo AI Chatbot

## Entity Relationships

```
[User] 1..* [Conversation] 1..* [Message]
[User] 1..* [Task] (existing from Phase II)
```

## Entity Definitions

### Conversation
**Description**: Represents a user's chat session with the AI, containing message history and context

**Fields**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table)
- `created_at`: DateTime (timestamp when conversation started)
- `updated_at`: DateTime (timestamp when last message was added)

**Validation rules**:
- `user_id` must reference an existing user
- `created_at` must be before `updated_at`
- User can only access conversations that belong to them

### Message
**Description**: Individual exchanges between user and AI, stored with timestamps and roles

**Fields**:
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to conversation)
- `role`: Enum (user|assistant|system)
- `content`: Text (the actual message content)
- `timestamp`: DateTime (when message was created)
- `sequence_number`: Integer (order of message in conversation)

**Validation rules**:
- `conversation_id` must reference an existing conversation
- `role` must be one of the allowed values (user, assistant, system)
- `sequence_number` must be unique within conversation
- `content` cannot be empty

### Task (Existing from Phase II)
**Description**: Task entity from Phase II, managed through MCP tools called by the AI agent

**Fields** (as defined in Phase II):
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table)
- `title`: String (task title)
- `description`: Text (optional task description)
- `status`: Enum (pending|completed)
- `created_at`: DateTime
- `updated_at`: DateTime

**Validation rules** (as defined in Phase II):
- `user_id` must reference an existing user
- `title` cannot be empty
- `status` must be one of the allowed values

## State Transitions

### Task States
```
PENDING → COMPLETED (via complete_task operation)
COMPLETED → PENDING (via update_task operation)
```

### Message Roles
```
USER → ASSISTANT (conversation flow)
SYSTEM → ASSISTANT (for bot-initiated messages)
```

## Indexes

### Conversation Table
- Index on `(user_id, created_at)` for efficient user conversation retrieval
- Index on `updated_at` for sorting by recency

### Message Table
- Index on `(conversation_id, sequence_number)` for ordered retrieval
- Index on `(conversation_id, timestamp)` for chronological access

### Task Table
- Index on `(user_id, status)` for efficient task filtering by user and status
- Index on `updated_at` for recency-based queries

## Constraints

### Referential Integrity
- Foreign key constraint: `messages.conversation_id` → `conversations.id`
- Foreign key constraint: `conversations.user_id` → `users.id`
- Foreign key constraint: `tasks.user_id` → `users.id`

### Data Consistency
- Conversation messages must belong to the same user as the conversation
- Task operations must be performed by the task owner
- Message content must not be empty

## Access Patterns

### Read Operations
1. Get all conversations for a user (sorted by last activity)
2. Get messages for a conversation (sorted by sequence)
3. Get tasks for a user (filtered by status)
4. Get conversation by ID with all messages

### Write Operations
1. Create new conversation
2. Add message to conversation
3. Update task via MCP tools
4. Mark task as completed via MCP tools

## Migration Considerations

### From Phase II
- Existing Task table remains unchanged
- New Conversation and Message tables will be added
- No breaking changes to existing task-related functionality

### API Integration
- Conversation and Message entities will be accessed via the new chat API endpoint
- MCP tools will operate on Task entities as before
- User authentication and authorization patterns remain consistent