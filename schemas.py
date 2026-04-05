from pydantic import BaseModel, EmailStr
from datetime import datetime


# ── Auth ──
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── User ──
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Client ──
class ClientCreate(BaseModel):
    client_name: str


class ClientUpdate(BaseModel):
    client_name: str | None = None


class ProjectBrief(BaseModel):
    id: int
    project_name: str

    model_config = {"from_attributes": True}


class ClientOut(BaseModel):
    id: int
    client_name: str
    created_at: datetime
    created_by: str  # user name
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClientDetailOut(BaseModel):
    id: int
    client_name: str
    created_at: datetime
    created_by: str
    updated_at: datetime | None = None
    projects: list[ProjectBrief] = []

    model_config = {"from_attributes": True}


# ── Project ──
class ProjectCreate(BaseModel):
    project_name: str
    client_id: int
    users: list[int]  # list of user IDs


class ProjectUserOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: int
    project_name: str
    client_id: int
    client_name: str
    created_at: datetime
    created_by: str
    users: list[ProjectUserOut] = []

    model_config = {"from_attributes": True}
