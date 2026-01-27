# Quickstart Guide: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-webapp
**Date**: 2026-01-05

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose
- Git

## Local Development Setup

### 1. Clone and Initialize Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
# Edit .env file with your configuration
```

Required environment variables:
- `DATABASE_URL`: Connection string for Neon PostgreSQL database
- `JWT_SECRET`: Secret key for JWT token generation
- `NEXTAUTH_SECRET`: Secret for NextAuth/Better Auth

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
# or
yarn install
```

### 5. Database Setup

Initialize the database using SQLModel:

```bash
cd backend
python -m src.main init-db
```

### 6. Running the Application

#### Option A: Development Mode (Separate Terminals)

Terminal 1 - Backend:
```bash
cd backend
python -m src.main
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# or
yarn dev
```

#### Option B: Using Docker Compose

```bash
docker-compose up --build
```

## Key Features Walkthrough

### 1. User Registration and Login
- Visit the registration page to create an account
- Use the login page to access your todo list
- Authentication is handled via JWT tokens

### 2. Task Management
- Create new tasks with title and description
- View all your tasks in the dashboard
- Update task details or mark as complete
- Delete tasks you no longer need

### 3. Data Isolation
- Each user only sees their own tasks
- Database-level isolation prevents cross-user access
- Authentication required for all task operations

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout user

### Tasks
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

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
# or
yarn test
```

### End-to-End Tests
```bash
cd frontend
npm run test:e2e
# or
yarn test:e2e
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure your Neon PostgreSQL connection string is correct
   - Verify database credentials in your environment file

2. **Authentication Problems**
   - Check that JWT secrets match between frontend and backend
   - Ensure Better Auth is properly configured

3. **Frontend/Backend Communication**
   - Verify API base URLs are correctly configured
   - Check that backend is running on the expected port

### Reset Development Environment

To reset your development environment:

```bash
# Stop all services
docker-compose down

# Clear any cached data
docker system prune -f

# Restart the application
docker-compose up --build
```

## Next Steps

1. Complete the registration and login flow
2. Create your first todo task
3. Explore the task management features
4. Review the complete feature specifications in `/specs/001-todo-fullstack-webapp/spec.md`