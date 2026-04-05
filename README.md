# Nimap Machine Test

FastAPI app for managing Users, Clients, and Projects with JWT auth.

Built using FastAPI + SQLAlchemy + PostgreSQL.

## How to run

### Prerequisites
- Python 3.10+
- PostgreSQL running locally

### Steps

```bash
# clone and enter the project
git clone https://github.com/SiddheshB5146/nimap_task.git
cd nimap_task

# install packages
pip install -r requirements.txt

# set up env
cp .env.example .env
# then edit .env and put your postgres username
```

Create the DB:
```bash
psql -h localhost -d postgres -c "CREATE DATABASE nimap_task;"
```

Run the server:
```bash
uvicorn main:app --reload
```

That's it. Go to http://localhost:8000/docs to test everything.

### Loading test data

If you want some sample data to play with:
```bash
python seed.py
```
This gives you 4 users, 3 clients, and 4 projects. All passwords are `password123`.

## Project structure

```
nimap_task/
├── main.py            - entry point, registers routers, creates tables
├── database.py        - postgres connection + session handling
├── models.py          - User, Client, Project tables (SQLAlchemy)
├── schemas.py         - request/response models (Pydantic)
├── auth.py            - JWT + bcrypt password stuff
├── seed.py            - script to load dummy data
├── requirements.txt
├── .env.example
└── routers/
    ├── users.py       - register + list users
    ├── auth_router.py - login endpoint
    ├── clients.py     - client CRUD
    └── projects.py    - project CRUD
```

## Relationships

- A client can have multiple projects
- A project belongs to one client
- A project can have multiple users assigned
- A user can be on multiple projects

## API endpoints

**Auth**
- `POST /auth/login` - login with email + password, get JWT token back

**Users**
- `POST /users/` - register
- `GET /users/` - list all

**Clients** (create/update/delete need auth)
- `POST /clients/` - create client
- `GET /clients/` - list all
- `GET /clients/{id}` - get client + its projects
- `PUT /clients/{id}` - update
- `DELETE /clients/{id}` - delete (returns 204)

**Projects** (all need auth)
- `POST /projects/` - create project, assign to client + users
- `GET /projects/` - list only YOUR assigned projects
- `DELETE /projects/{id}` - delete (returns 204)

## How to test in Swagger

1. Open http://localhost:8000/docs
2. Register a user via `POST /users/`
3. Login via `POST /auth/login` — copy the `access_token` from response
4. Click the **Authorize** button (top right), paste the token, click Authorize
5. Now all the protected endpoints will work

If you ran `seed.py`, you can skip registration and directly login with:
- `rohit@example.com` / `password123`
- `sneha@example.com` / `password123`
- `amit@example.com` / `password123`
- `priya@example.com` / `password123`

## Test data details (seed.py)

**Users:** Rohit, Sneha, Amit, Priya

**Clients:** Nimap Infotech (by Rohit), TCS (by Sneha), Infosys (by Rohit)

**Projects:**

| Project | Client | Users assigned | Created by |
|---------|--------|---------------|------------|
| E-Commerce Platform | Nimap Infotech | Rohit, Sneha | Rohit |
| Banking App | TCS | Sneha, Amit | Sneha |
| HR Portal | Nimap Infotech | Rohit, Amit, Priya | Rohit |
| Cloud Migration | Infosys | Amit, Priya | Amit |

So when you login as Rohit and hit `GET /projects/`, you'll only see E-Commerce Platform and HR Portal (the two he's assigned to). Login as Amit and you'll see Banking App, HR Portal, and Cloud Migration instead.
