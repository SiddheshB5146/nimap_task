from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Validate client exists
    client = db.query(models.Client).filter(models.Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate all users exist
    users = db.query(models.User).filter(models.User.id.in_(payload.users)).all()
    if len(users) != len(payload.users):
        raise HTTPException(status_code=400, detail="One or more users not found")

    project = models.Project(
        project_name=payload.project_name,
        client_id=payload.client_id,
        created_by_id=current_user.id,
        users=users,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_out(project)


@router.get("/", response_model=list[schemas.ProjectOut])
def list_my_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    projects = (
        db.query(models.Project)
        .filter(models.Project.users.any(models.User.id == current_user.id))
        .all()
    )
    return [_project_to_out(p) for p in projects]


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None


def _project_to_out(project: models.Project) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id=project.id,
        project_name=project.project_name,
        client_id=project.client_id,
        client_name=project.client.client_name,
        created_at=project.created_at,
        created_by=project.created_by.name,
        users=[schemas.ProjectUserOut(id=u.id, name=u.name) for u in project.users],
    )
