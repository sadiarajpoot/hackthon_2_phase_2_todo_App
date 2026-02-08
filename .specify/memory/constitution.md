<!-- SYNC IMPACT REPORT
Version change: 1.0.0 → 1.1.0 (Minor: Phase III addition)
Modified principles: Updated all to include Phase III scope
Added sections: AI Chatbot principles, MCP tools, Conversation persistence
Removed sections: N/A
Templates requiring updates:
- ✅ .specify/templates/plan-template.md (Constitution Check section will align)
- ✅ .specify/templates/spec-template.md (Requirements section aligned)
- ✅ .specify/templates/tasks-template.md (Task categorization reflects principles)
Templates: All checked and aligned with new principles
Follow-up TODOs: None
-->
# Hackathon II: Todo Full-Stack Web Application + AI Chatbot (Phase II + III) Constitution

## Core Principles

### Spec-driven development using Spec-Kit Plus and Claude Code
All development follows spec-driven approach using Spec-Kit Plus and Claude Code; Every feature must have clear specifications before implementation; Adherence to defined architecture and implementation patterns; Both Phase II and Phase III features follow spec-driven methodology

### Security-first approach with user isolation and JWT authentication
All features must implement security from the ground up; User data isolation is mandatory; JWT authentication required for all endpoints; Zero tolerance for security vulnerabilities; Authentication remains consistent across both Phase II and Phase III components

### Phase Isolation and Backwards Compatibility
Phase III additions must not break Phase II functionality; New AI chatbot features extend but do not alter existing Phase II core functionality; Both phases remain fully functional independently; Changes to shared components must maintain backward compatibility

### Stateless AI Architecture with Persistent Conversations
Chatbot server operates in stateless manner; Conversation history persists in database; MCP tools enable natural language task management; Friendly confirmations and error handling required; Resume conversations after server restart capability

### Scalability through serverless technologies and modern frameworks
Leverage serverless technologies for automatic scaling; Use modern frameworks for optimal performance; Design for horizontal scaling and resource efficiency; Support both traditional web interface and AI chatbot traffic patterns

### Maintainability with organized monorepo structure and clear documentation
Maintain organized monorepo structure with clear separation of concerns; All code must be well-documented with clear comments; Follow consistent coding standards across the codebase; Clear distinction between Phase II and Phase III components

### Full-stack integration with Next.js, FastAPI, and AI Components
Frontend built with Next.js 16+ using App Router for traditional interface; OpenAI ChatKit UI for chatbot interface; Backend built with FastAPI for API endpoints; AI Logic powered by OpenAI Agents SDK and MCP tools

### Quality assurance with comprehensive testing
Unit tests for all API endpoints; Integration tests for authentication flows; End-to-end testing for task CRUD operations; Test coverage metrics maintained; Testing includes both traditional and AI-driven interactions

## Technology Stack and Standards

Next.js 16+ (App Router), FastAPI, SQLModel, Neon Serverless PostgreSQL, Better Auth, OpenAI ChatKit, OpenAI Agents SDK, MCP tools; TypeScript with Tailwind for frontend; Python with Pydantic for backend; AI components use stateless architecture with DB persistence; All features must reference specs in /specs/ directory including @specs/chatbot.md, @specs/mcp-tools.md, @specs/chat-api.md

## Development Workflow

Monorepo setup with docker-compose for development; Spec-driven development using Spec-Kit Plus for both phases; All changes require unit and integration tests; Documentation updated for every change; Phase III implementation occurs after Phase II verification; MCP tools enable AI-driven task operations

## Governance

All features must implement 5 basic CRUD operations plus authentication in Phase II; Phase III extends functionality with natural language task management (create, list, update, complete, delete); Code format follows frontend (TypeScript with Tailwind) and backend (Python with Pydantic) conventions; Zero critical bugs in auth or data handling; Successful end-to-end testing required for both phases; Phase III must not compromise Phase II functionality

**Version**: 1.1.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-28