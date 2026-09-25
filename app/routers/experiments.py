from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.deps import get_db
from app.models import ExperimentStatus

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=list[schemas.ExperimentRead])
def list_experiments(
    status_filter: ExperimentStatus | None = Query(default=None, alias="status"),
    model_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    status_value = status_filter.value if status_filter else None
    return crud.get_experiments(db, status=status_value, model_id=model_id)


@router.get("/{experiment_id}", response_model=schemas.ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = crud.get_experiment(db, experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.post("", response_model=schemas.ExperimentRead, status_code=status.HTTP_201_CREATED)
def create_experiment(payload: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    return crud.create_experiment(db, payload)


@router.patch("/{experiment_id}", response_model=schemas.ExperimentRead)
def update_experiment(
    experiment_id: int,
    payload: schemas.ExperimentUpdate,
    db: Session = Depends(get_db),
):
    exp = crud.get_experiment(db, experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return crud.update_experiment(db, exp, payload)


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = crud.get_experiment(db, experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    crud.delete_experiment(db, exp)