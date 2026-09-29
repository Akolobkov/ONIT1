from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.exceptions import BusinessRuleError
from app.models import TaskStatus
import app.schemas.model_schema as schema
def get_models(
    db: Session,
    framework: str | None = None,
    task_id: int | None = None,
) -> list[models.Model]:
    stmt = select(models.Model)
    if framework is not None:
        stmt = stmt.where(models.Model.framework == framework)
    if task_id is not None:
        stmt = stmt.where(models.Model.task_id == task_id)
    return list(db.scalars(stmt).all())


def get_model(db: Session, model_id: int) -> models.Model | None:
    return db.get(models.Model, model_id)


def create_model(db: Session, data: schema.ModelCreate) -> models.Model:
    task = db.get(models.Task, data.task_id)
    if task is None:
        raise BusinessRuleError(f"Задача id={data.task_id} не найдена")

    # БП-1: нельзя добавлять модель в завершённую задачу
    if task.status == TaskStatus.DONE.value:
        raise BusinessRuleError(
            f"Нельзя добавить модель в задачу id={task.id} со статусом 'done'"
        )

    model = models.Model(
        name=data.name,
        framework=data.framework.value,
        task_id=data.task_id,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_model(db: Session, model: models.Model, data: schema.ModelUpdate) -> models.Model:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if field == "framework":
            value = value.value
        setattr(model, field, value)
    db.commit()
    db.refresh(model)
    return model


def delete_model(db: Session, model: models.Model) -> None:
    db.delete(model)
    db.commit()
