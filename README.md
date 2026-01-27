---
title: Todo App Backend
emoji: 🚀
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
python_version: "3.9"
---

# Todo Full-Stack Web Application

A multi-user todo web application with JWT authentication and user data isolation. The application follows a monorepo architecture with Next.js frontend and FastAPI backend, using Neon PostgreSQL for persistence and Better Auth for authentication. The system supports full CRUD operations on tasks with proper user isolation.

## Features

- User registration and authentication with JWT tokens
- Create, read, update, and delete tasks
- Toggle task completion status
- User data isolation - users only see their own tasks
- Responsive web interface
- RESTful API design

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLModel
- Neon Serverless PostgreSQL
- Better Auth for JWT authentication
- Pydantic for data validation

### Frontend
- Next.js 14
- React 18
- Tailwind CSS
- TypeScript

### Infrastructure
- Docker & Docker Compose
- JWT-based authentication

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- Git

### Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   - Set `JWT_SECRET` to a secure random string
   - Configure database connection if not using Docker

### Running the Application

#### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs

#### Option 2: Local Development

1. Backend setup:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

2. Frontend setup:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks` - Get all tasks for the authenticated user
- `POST /api/tasks` - Create a new task for the authenticated user
- `GET /api/tasks/{id}` - Get a specific task by ID
- `PUT /api/tasks/{id}` - Update a specific task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion status of a task
- `DELETE /api/tasks/{id}` - Delete a specific task

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── models/         # SQLModel database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── api/            # API routers
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Backend tests
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node.js dependencies
│   └── tests/              # Frontend tests
├── docker-compose.yml      # Docker configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Security

- JWT-based authentication
- Passwords are securely hashed using bcrypt
- User data isolation at the application level
- Input validation using Pydantic
- Protection against common web vulnerabilities

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Development

This project follows a spec-driven development approach. All features are specified in the `/specs` directory before implementation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.