"""
Seed script — populates the database with dummy data.
Run: python seed.py
"""

from database import SessionLocal, engine, Base
from models import User, Client, Project
from auth import hash_password

# Recreate all tables (fresh start)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── 1. Create Users ──
users = [
    User(name="Rohit", email="rohit@example.com", password=hash_password("password123")),
    User(name="Sneha", email="sneha@example.com", password=hash_password("password123")),
    User(name="Amit", email="amit@example.com", password=hash_password("password123")),
    User(name="Priya", email="priya@example.com", password=hash_password("password123")),
]
db.add_all(users)
db.commit()
for u in users:
    db.refresh(u)
print(f"Created {len(users)} users")

# ── 2. Create Clients ──
clients = [
    Client(client_name="Nimap Infotech", created_by_id=users[0].id),
    Client(client_name="TCS", created_by_id=users[1].id),
    Client(client_name="Infosys", created_by_id=users[0].id),
]
db.add_all(clients)
db.commit()
for c in clients:
    db.refresh(c)
print(f"Created {len(clients)} clients")

# ── 3. Create Projects ──
projects = [
    Project(
        project_name="E-Commerce Platform",
        client_id=clients[0].id,       # Nimap Infotech
        created_by_id=users[0].id,      # Rohit
        users=[users[0], users[1]],     # Rohit, Sneha
    ),
    Project(
        project_name="Banking App",
        client_id=clients[1].id,        # TCS
        created_by_id=users[1].id,      # Sneha
        users=[users[1], users[2]],     # Sneha, Amit
    ),
    Project(
        project_name="HR Portal",
        client_id=clients[0].id,        # Nimap Infotech
        created_by_id=users[0].id,      # Rohit
        users=[users[0], users[2], users[3]],  # Rohit, Amit, Priya
    ),
    Project(
        project_name="Cloud Migration",
        client_id=clients[2].id,        # Infosys
        created_by_id=users[2].id,      # Amit
        users=[users[2], users[3]],     # Amit, Priya
    ),
]
db.add_all(projects)
db.commit()
print(f"Created {len(projects)} projects")

db.close()

print("\n--- Dummy Data Summary ---")
print("Users:    Rohit, Sneha, Amit, Priya  (password: password123)")
print("Clients:  Nimap Infotech, TCS, Infosys")
print("Projects: E-Commerce Platform, Banking App, HR Portal, Cloud Migration")
print("\nLogin with any user email + password123 to test the API.")
