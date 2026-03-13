# Example Plan Output

This is an example output from the Plan prompt for a Task Management API.

---

## Task Graph

```json
{
  "current_task_id": null,
  "backlog": [
    {
      "id": "task-1",
      "title": "Create database base and connection",
      "description": "Set up SQLAlchemy Base class, database engine, and session factory. Create get_db dependency for FastAPI.",
      "status": "pending",
      "priority": "high",
      "files": ["src/models/base.py"],
      "dependencies": []
    },
    {
      "id": "task-2",
      "title": "Create User model",
      "description": "Define User SQLAlchemy model with id, email, hashed_password, created_at fields. Include relationship to tasks.",
      "status": "pending",
      "priority": "high",
      "files": ["src/models/user.py"],
      "dependencies": ["task-1"]
    },
    {
      "id": "task-3",
      "title": "Create Task model",
      "description": "Define Task SQLAlchemy model with id, title, description, status, user_id, timestamps. Include foreign key to User.",
      "status": "pending",
      "priority": "high",
      "files": ["src/models/task.py"],
      "dependencies": ["task-1"]
    },
    {
      "id": "task-4",
      "title": "Create Pydantic schemas",
      "description": "Define request/response schemas: UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse, Token.",
      "status": "pending",
      "priority": "high",
      "files": ["src/schemas/schemas.py"],
      "dependencies": []
    },
    {
      "id": "task-5",
      "title": "Implement JWT authentication",
      "description": "Create functions for JWT token creation, verification, and password hashing. Include get_current_user dependency.",
      "status": "pending",
      "priority": "high",
      "files": ["src/auth/jwt.py"],
      "dependencies": ["task-2"]
    },
    {
      "id": "task-6",
      "title": "Implement UserService",
      "description": "Create UserService class with create, authenticate, and get_by_id methods. Handle password hashing.",
      "status": "pending",
      "priority": "high",
      "files": ["src/services/user_service.py"],
      "dependencies": ["task-2", "task-5"]
    },
    {
      "id": "task-7",
      "title": "Implement TaskService",
      "description": "Create TaskService class with CRUD methods: create, list, get, update, delete. Filter by user_id.",
      "status": "pending",
      "priority": "medium",
      "files": ["src/services/task_service.py"],
      "dependencies": ["task-3"]
    },
    {
      "id": "task-8",
      "title": "Create auth routes",
      "description": "Define /register and /login endpoints. Return JWT token on successful authentication.",
      "status": "pending",
      "priority": "medium",
      "files": ["src/routes/auth.py"],
      "dependencies": ["task-4", "task-6"]
    },
    {
      "id": "task-9",
      "title": "Create task routes",
      "description": "Define CRUD endpoints for tasks: POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}.",
      "status": "pending",
      "priority": "medium",
      "files": ["src/routes/tasks.py"],
      "dependencies": ["task-4", "task-5", "task-7"]
    },
    {
      "id": "task-10",
      "title": "Create main application",
      "description": "Set up FastAPI app, include routers, configure CORS, create database tables on startup.",
      "status": "pending",
      "priority": "medium",
      "files": ["src/main.py"],
      "dependencies": ["task-8", "task-9"]
    },
    {
      "id": "task-11",
      "title": "Add model unit tests",
      "description": "Write tests for User and Task models: creation, relationships, constraints.",
      "status": "pending",
      "priority": "medium",
      "files": ["tests/test_models.py"],
      "dependencies": ["task-2", "task-3"]
    },
    {
      "id": "task-12",
      "title": "Add auth integration tests",
      "description": "Test /register and /login endpoints: success cases, validation errors, duplicate email.",
      "status": "pending",
      "priority": "low",
      "files": ["tests/test_auth.py"],
      "dependencies": ["task-10"]
    },
    {
      "id": "task-13",
      "title": "Add task integration tests",
      "description": "Test task CRUD endpoints: authentication required, ownership checks, not found cases.",
      "status": "pending",
      "priority": "low",
      "files": ["tests/test_tasks.py"],
      "dependencies": ["task-10", "task-12"]
    }
  ]
}
```

## Build Order

| Order | Task ID | Title | Why This Order |
|-------|---------|-------|----------------|
| 1 | task-1 | Create database base | Foundation - no dependencies |
| 2 | task-4 | Create Pydantic schemas | Foundation - no dependencies |
| 3 | task-2 | Create User model | Needs task-1 (Base) |
| 4 | task-3 | Create Task model | Needs task-1 (Base) |
| 5 | task-5 | Implement JWT auth | Needs task-2 (User) |
| 6 | task-6 | Implement UserService | Needs task-2, task-5 |
| 7 | task-7 | Implement TaskService | Needs task-3 |
| 8 | task-8 | Create auth routes | Needs task-4, task-6 |
| 9 | task-9 | Create task routes | Needs task-4, task-5, task-7 |
| 10 | task-10 | Create main application | Needs task-8, task-9 |
| 11 | task-11 | Add model tests | Needs task-2, task-3 |
| 12 | task-12 | Add auth tests | Needs task-10 |
| 13 | task-13 | Add task tests | Needs task-10, task-12 |

## File → Task Mapping

| File Path | Task | Purpose |
|-----------|------|---------|
| src/models/base.py | task-1 | Database foundation |
| src/models/user.py | task-2 | User data model |
| src/models/task.py | task-3 | Task data model |
| src/schemas/schemas.py | task-4 | API schemas |
| src/auth/jwt.py | task-5 | Authentication |
| src/services/user_service.py | task-6 | User business logic |
| src/services/task_service.py | task-7 | Task business logic |
| src/routes/auth.py | task-8 | Auth endpoints |
| src/routes/tasks.py | task-9 | Task endpoints |
| src/main.py | task-10 | Application entry |
| tests/test_models.py | task-11 | Model tests |
| tests/test_auth.py | task-12 | Auth tests |
| tests/test_tasks.py | task-13 | Task tests |

## Scaffolding Specification

```
task-api/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── task_service.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       └── tasks.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_auth.py
│   └── test_tasks.py
├── requirements.txt
└── README.md
```

## Reference Map Seed

```json
{
  "modules": {
    "models.base": {
      "file_path": "src/models/base.py",
      "classes": ["Base"],
      "functions": ["get_db"],
      "exports": ["Base", "get_db", "engine", "SessionLocal"]
    }
  },
  "public_api": {
    "models": ["User", "Task", "Base"],
    "services": ["UserService", "TaskService"],
    "auth": ["create_token", "verify_token", "get_current_user"]
  },
  "cross_module_deps": {
    "services.user_service": ["models.user", "auth.jwt"],
    "services.task_service": ["models.task"],
    "routes.auth": ["services.user_service", "schemas"],
    "routes.tasks": ["services.task_service", "auth.jwt", "schemas"]
  }
}
```

## MVP Completion Checklist

When these tasks are done, MVP is complete:

- [ ] task-1 through task-10 completed (core functionality)
- [ ] task-11 through task-13 completed (test coverage)
- [ ] All tests passing
- [ ] User can register and login
- [ ] User can CRUD their tasks
- [ ] Unauthorized requests return 401
- [ ] Not found returns 404

---

## Claude Code Instructions

When you paste this plan into Claude Code, run:

```
/import-plan
```

This will:
1. Parse the task graph into tasks_queue.json
2. Create directory scaffolding
3. Update architecture.md
4. Seed reference_map.json
5. Auto-run /boot to start your session

Then run `/next` to begin task-1.
