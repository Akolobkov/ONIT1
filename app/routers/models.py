from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.deps import get_db
from app.models import Framework

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[schemas.ModelRead])
def list_models(
    framework: Framework | None = Query(default=None),
    task_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    framework_value = framework.value if framework else None
    return crud.get_models(db, framework=framework_value, task_id=task_id)


@router.get("/{model_id}", response_model=schemas.ModelRead)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = crud.get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("", response_model=schemas.ModelRead, status_code=status.HTTP_201_CREATED)
def create_model(payload: schemas.ModelCreate, db: Session = Depends(get_db)):
    return crud.create_model(db, payload)


@router.patch("/{model_id}", response_model=schemas.ModelRead)
def update_model(model_id: int, payload: schemas.ModelUpdate, db: Session = Depends(get_db)):
    model = crud.get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return crud.update_model(db, model, payload)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    model = crud.get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    crud.delete_model(db, model)