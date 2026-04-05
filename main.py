from fastapi import FastAPI
from database import engine, Base
from routers import users, auth_router, clients, projects

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nimap Machine Test", version="1.0.0")

app.include_router(users.router)
app.include_router(auth_router.router)
app.include_router(clients.router)
app.include_router(projects.router)


@app.get("/")
def root():
    return {"message": "Nimap Machine Test API — visit /docs for Swagger UI"}


