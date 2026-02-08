# Quickstart Guide: AI Chatbot for Todo Management

## Overview
This guide provides the essential steps to set up and run the AI Chatbot feature for managing todos via natural language.

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon Serverless PostgreSQL for cloud deployment)
- OpenAI API key
- Better Auth configured (existing from Phase II)

## Environment Setup

### Backend Configuration
1. Set up environment variables in your `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
JWT_SECRET=your_jwt_secret_from_phase_ii
```

### Frontend Configuration
1. Set up environment variables in your frontend `.env.local`:
```bash
NEXT_PUBLIC_CHAT_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Database Setup
```bash
# Run migrations to create conversation and message tables
cd backend
python -m alembic upgrade head
```

### 3. Start Services
```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## API Endpoints

### Chat Endpoint
- **POST** `/api/{user_id}/chat`
- Send natural language commands to the AI chatbot
- Example: `"Add a task to buy groceries"`

### Conversations Endpoints
- **GET** `/api/{user_id}/conversations` - List user's conversations
- **GET** `/api/{user_id}/conversations/{conversation_id}` - Get specific conversation

## Using the Chat Interface

1. Navigate to the chat page in the frontend application
2. Authenticate using the existing Better Auth system
3. Type natural language commands like:
   - "Add a task to buy groceries"
   - "Show all tasks"
   - "Mark task 3 as complete"
   - "Update task 1 title to 'Call mom'"
   - "Delete task 2"

## Testing

### Backend Tests
```bash
# Run all backend tests
cd backend
pytest

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
```

### Frontend Tests
```bash
# Run frontend tests
cd frontend
npm test
```

## Key Components

### MCP Tools Integration
- Located in `backend/src/agents/mcp_tools.py`
- Maps natural language commands to task operations
- Handles create, read, update, delete, and complete operations

### Conversation Service
- Located in `backend/src/services/conversation_service.py`
- Manages conversation history persistence
- Ensures stateless operation with database storage

### Chat API
- Located in `backend/src/api/chat.py`
- Handles chat requests and responses
- Integrates with MCP tools and conversation service

## Troubleshooting

### Common Issues
- **Authentication errors**: Ensure JWT tokens are properly configured from Phase II
- **Database connection**: Verify DATABASE_URL is correct
- **OpenAI API errors**: Check OPENAI_API_KEY is valid and has sufficient quota

### Logs
- Backend logs: Check console output from uvicorn
- Frontend logs: Check browser console and Next.js output