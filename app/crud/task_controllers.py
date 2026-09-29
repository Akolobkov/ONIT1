from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.exceptions import BusinessRuleError
from app.models import ExperimentStatus, TaskStatus
import app.schemas.task_schema as schema

def get_tasks(db: Session, status: TaskStatus | None = None) -> list[models.Task]:
    stmt = select(models.Task)
    if status is not None:
        stmt = stmt.where(models.Task.status == status.value)
    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.get(models.Task, task_id)


def create_task(db: Session, data: schema.TaskCreate) -> models.Task:
    task = models.Task(
        title=data.title,
        description=data.description,
        status=data.status.value,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: models.Task, data: schema.TaskUpdate) -> models.Task:
    # БП-5: перевод в done требует finished-эксперимента у каждой модели
    if data.status == TaskStatus.DONE and task.status != TaskStatus.DONE.value:
        _ensure_all_models_have_finished_experiment(task)

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if field == "status":
            value = value.value
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    # БП-4: нельзя удалять задачу с running-экспериментом
    for model in task.models:
        for exp in model.experiments:
            if exp.status == ExperimentStatus.RUNNING.value:
                raise BusinessRuleError(
                    f"Нельзя удалить задачу id={task.id}: "
                    f"у модели id={model.id} есть running-эксперимент id={exp.id}"
                )
    db.delete(task)
    db.commit()


def _ensure_all_models_have_finished_experiment(task: models.Task) -> None:
    if not task.models:
        raise BusinessRuleError(
            f"Нельзя завершить задачу id={task.id}: у неё нет ни одной модели"
        )
    for model in task.models:
        has_finished = any(
            exp.status == ExperimentStatus.FINISHED.value and exp.accuracy is not None
            for exp in model.experiments
        )
        if not has_finished:
            raise BusinessRuleError(
                f"Нельзя завершить задачу id={task.id}: "
                f"у модели id={model.id} нет завершённого эксперимента с accuracy"
            )
