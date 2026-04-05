# How to Run - Nimap Task API

## Prerequisites
- Python 3.10+
- PostgreSQL running locally

## Setup

### 1. Install Dependencies
```bash
cd nimap_task
pip install -r requirements.txt
```

### 2. Configure Database
Update `.env` with your PostgreSQL credentials:
```
DATABASE_URL=postgresql+pg8000://<username>@localhost:5432/nimap_task
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Create the Database
```bash
psql -h localhost -d postgres -c "CREATE DATABASE nimap_task;"
```
Tables are auto-created when the server starts.

### 4. Load Dummy Data (Optional)
```bash
python seed.py
```
This creates the following test data:

| Users (password: `password123` for all) | Clients         | Projects             |
|-----------------------------------------|-----------------|----------------------|
| Rohit (rohit@example.com)               | Nimap Infotech  | E-Commerce Platform  |
| Sneha (sneha@example.com)               | TCS             | Banking App          |
| Amit (amit@example.com)                 | Infosys         | HR Portal            |
| Priya (priya@example.com)               |                 | Cloud Migration      |

**Project assignments:**
| Project              | Client         | Assigned Users        | Created By |
|----------------------|----------------|-----------------------|------------|
| E-Commerce Platform  | Nimap Infotech | Rohit, Sneha          | Rohit      |
| Banking App          | TCS            | Sneha, Amit           | Sneha      |
| HR Portal            | Nimap Infotech | Rohit, Amit, Priya    | Rohit      |
| Cloud Migration      | Infosys        | Amit, Priya           | Amit       |

### 5. Start the Server
```bash
uvicorn main:app --reload
```
Server runs at `http://localhost:8000`

---

## API Testing (Swagger UI)

Open `http://localhost:8000/docs` in your browser.

---

## File-by-File Explanation (with Dummy Data Examples)

### `database.py` — Database Connection
Connects to PostgreSQL and provides a `get_db()` function that gives each API request its own database session. FastAPI's dependency injection calls this automatically — you never open/close connections manually.

### `models.py` — Database Tables (SQLAlchemy ORM)
Defines 4 tables and their relationships:

```
users           clients              projects          project_user (M2M)
------          --------             ---------         ------------------
id: 1           id: 1                id: 1             project_id: 1, user_id: 1
name: Rohit     client_name: Nimap   project_name:     project_id: 1, user_id: 2
email: ...      created_by_id: 1       E-Commerce      project_id: 2, user_id: 2
password: ...   created_at: ...      client_id: 1      project_id: 2, user_id: 3
                                     created_by_id: 1  ...
```

**Key relationships:**
- A Client has many Projects → Nimap Infotech has "E-Commerce Platform" + "HR Portal"
- A Project belongs to one Client → "Banking App" belongs only to TCS
- A Project has many Users (M2M) → "HR Portal" has Rohit, Amit, Priya
- A User can be in many Projects → Amit is in "Banking App", "HR Portal", "Cloud Migration"

### `schemas.py` — Request/Response Validation (Pydantic)
Controls what data goes in and out of the API. For example:
- **Input** (UserCreate): `{"name": "Rohit", "email": "rohit@example.com", "password": "password123"}`
- **Output** (UserOut): `{"id": 1, "name": "Rohit", "email": "rohit@example.com", "created_at": "..."}` — password is never returned.

### `auth.py` — JWT Authentication
Handles password hashing and JWT tokens:
1. When Rohit registers → password "password123" is hashed with bcrypt and stored
2. When Rohit logs in → password is verified, a JWT token is created containing `{"sub": "1"}` (his user ID)
3. When Rohit hits a protected endpoint → the token is decoded, user ID extracted, and Rohit's User object is loaded from DB

### `routers/users.py` — User Endpoints

**POST /users/** — Register a new user
```
Input:  {"name": "Rohit", "email": "rohit@example.com", "password": "password123"}
Output: {"id": 1, "name": "Rohit", "email": "rohit@example.com", "created_at": "..."}
```
- Checks if email already exists (returns 400 if duplicate)
- Hashes the password before storing

**GET /users/** — List all users
```
Output: [
  {"id": 1, "name": "Rohit", "email": "rohit@example.com", ...},
  {"id": 2, "name": "Sneha", "email": "sneha@example.com", ...},
  {"id": 3, "name": "Amit", "email": "amit@example.com", ...},
  {"id": 4, "name": "Priya", "email": "priya@example.com", ...}
]
```

### `routers/auth_router.py` — Login Endpoint

**POST /auth/login** — Get JWT token
```
Input:  {"email": "rohit@example.com", "password": "password123"}
Output: {"access_token": "eyJhbGciOi...", "token_type": "bearer"}
```
- Verifies email exists and password matches
- Returns JWT token valid for 30 minutes
- Use this token in the "Authorize" button in Swagger, or as `Authorization: Bearer <token>` header

### `routers/clients.py` — Client CRUD

**POST /clients/** (Auth required) — Create a client
```
Input:  {"client_name": "Nimap Infotech"}
Output: {"id": 1, "client_name": "Nimap Infotech", "created_by": "Rohit", "created_at": "...", "updated_at": "..."}
```
- `created_by` is auto-set from the logged-in user's name

**GET /clients/** — List all clients
```
Output: [
  {"id": 1, "client_name": "Nimap Infotech", "created_by": "Rohit", ...},
  {"id": 2, "client_name": "TCS", "created_by": "Sneha", ...},
  {"id": 3, "client_name": "Infosys", "created_by": "Rohit", ...}
]
```

**GET /clients/1** — Client detail WITH its projects
```
Output: {
  "id": 1,
  "client_name": "Nimap Infotech",
  "created_by": "Rohit",
  "projects": [
    {"id": 1, "project_name": "E-Commerce Platform"},
    {"id": 3, "project_name": "HR Portal"}
  ]
}
```
- This is where you see the one-to-many relationship: Nimap has 2 projects

**PUT /clients/1** (Auth required) — Update client name
```
Input:  {"client_name": "Nimap Infotech Pvt Ltd"}
Output: {"id": 1, "client_name": "Nimap Infotech Pvt Ltd", "updated_at": "<new timestamp>", ...}
```

**DELETE /clients/1** (Auth required) — Delete client
```
Response: 204 No Content (empty body)
```
- Also deletes all projects under that client (cascade delete)

### `routers/projects.py` — Project CRUD

**POST /projects/** (Auth required) — Create a project
```
Input:  {"project_name": "E-Commerce Platform", "client_id": 1, "users": [1, 2]}
Output: {
  "id": 1,
  "project_name": "E-Commerce Platform",
  "client_id": 1,
  "client_name": "Nimap Infotech",
  "created_by": "Rohit",
  "users": [{"id": 1, "name": "Rohit"}, {"id": 2, "name": "Sneha"}]
}
```
- Validates that client_id exists (returns 404 if not)
- Validates all user IDs exist (returns 400 if any missing)
- `users` field assigns users to the project (many-to-many)

**GET /projects/** (Auth required) — List MY projects only
```
Logged in as Rohit → sees E-Commerce Platform + HR Portal (2 projects)
Logged in as Sneha → sees E-Commerce Platform + Banking App (2 projects)
Logged in as Amit  → sees Banking App + HR Portal + Cloud Migration (3 projects)
Logged in as Priya → sees HR Portal + Cloud Migration (2 projects)
```
- Each user ONLY sees projects they are assigned to
- Response includes client_name and assigned users list

**DELETE /projects/1** (Auth required) — Delete project
```
Response: 204 No Content (empty body)
```

### `seed.py` — Dummy Data Loader
Drops all tables, recreates them, and inserts 4 users, 3 clients, and 4 projects with proper relationships. Run `python seed.py` anytime to reset to a clean state with fresh dummy data.

### `main.py` — App Entry Point
Creates the FastAPI app, auto-creates tables, and includes all 4 routers (users, auth, clients, projects). The `/docs` endpoint gives you Swagger UI for free.

---

## Quick Test Flow (after running seed.py)

1. Open `http://localhost:8000/docs`
2. Try `GET /users/` — see all 4 users
3. Try `GET /clients/` — see all 3 clients
4. Hit `POST /auth/login` with `{"email": "rohit@example.com", "password": "password123"}`
5. Copy the token → Click "Authorize" button → Paste it → Click "Authorize"
6. Try `GET /projects/` — see only Rohit's 2 projects (E-Commerce Platform, HR Portal)
7. Try `GET /clients/1` — see Nimap Infotech with its 2 projects listed
8. Logout, login as Sneha, and `GET /projects/` — different projects appear (E-Commerce Platform, Banking App)
