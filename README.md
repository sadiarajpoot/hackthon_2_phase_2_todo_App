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

## Deployment

### Frontend Deployment (Vercel)

To deploy the frontend to Vercel:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

3. Deploy to Vercel:
   ```bash
   vercel --prod
   ```

### Backend Deployment

The backend needs to be deployed to a Python-compatible platform like Render, Railway, or Heroku:

#### Option 1: Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the runtime to Python
4. Set the build command to: `pip install -r requirements.txt`
5. Set the start command to: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

#### Option 2: Deploy to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set the deploy directory to `backend`
4. Add the environment variables from your `.env` file

### Environment Variables

When deploying, make sure to set the following environment variables:

- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `JWT_SECRET`: Secure secret for JWT tokens
- `NEXTAUTH_SECRET`: Secret for NextAuth
- `NEXT_PUBLIC_API_URL`: URL of your deployed backend API

## Development

This project follows a spec-driven development approach. All features are specified in the `/specs` directory before implementation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.