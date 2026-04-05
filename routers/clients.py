from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=schemas.ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = models.Client(
        client_name=payload.client_name,
        created_by_id=current_user.id,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return _client_to_out(client)


@router.get("/", response_model=list[schemas.ClientOut])
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(models.Client).all()
    return [_client_to_out(c) for c in clients]


@router.get("/{client_id}", response_model=schemas.ClientDetailOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return schemas.ClientDetailOut(
        id=client.id,
        client_name=client.client_name,
        created_at=client.created_at,
        updated_at=client.updated_at,
        created_by=client.created_by.name,
        projects=[schemas.ProjectBrief(id=p.id, project_name=p.project_name) for p in client.projects],
    )


@router.put("/{client_id}", response_model=schemas.ClientOut)
def update_client(
    client_id: int,
    payload: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if payload.client_name is not None:
        client.client_name = payload.client_name

    db.commit()
    db.refresh(client)
    return _client_to_out(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return None


def _client_to_out(client: models.Client) -> schemas.ClientOut:
    return schemas.ClientOut(
        id=client.id,
        client_name=client.client_name,
        created_at=client.created_at,
        updated_at=client.updated_at,
        created_by=client.created_by.name,
    )
