from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.exceptions import BusinessRuleError
from app.models import ExperimentStatus, TaskStatus
import app.schemas.experiment_schema as schema
def get_experiments(
    db: Session,
    status: str | None = None,
    model_id: int | None = None,
) -> list[models.Experiment]:
    stmt = select(models.Experiment)
    if status is not None:
        stmt = stmt.where(models.Experiment.status == status)
    if model_id is not None:
        stmt = stmt.where(models.Experiment.model_id == model_id)
    return list(db.scalars(stmt).all())


def get_experiment(db: Session, experiment_id: int) -> models.Experiment | None:
    return db.get(models.Experiment, experiment_id)


def create_experiment(db: Session, data: schema.ExperimentCreate) -> models.Experiment:
    model = db.get(models.Model, data.model_id)
    if model is None:
        raise BusinessRuleError(f"Модель id={data.model_id} не найдена")

    # БП-2: у модели не может быть двух running-экспериментов
    if data.status == ExperimentStatus.RUNNING:
        existing_running = db.scalar(
            select(models.Experiment).where(
                models.Experiment.model_id == data.model_id,
                models.Experiment.status == ExperimentStatus.RUNNING.value,
            )
        )
        if existing_running is not None:
            raise BusinessRuleError(
                f"У модели id={data.model_id} уже есть running-эксперимент "
                f"id={existing_running.id}"
            )

    experiment = models.Experiment(
        name=data.name,
        status=data.status.value,
        accuracy=data.accuracy,
        model_id=data.model_id,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def update_experiment(
    db: Session,
    experiment: models.Experiment,
    data: schema.ExperimentUpdate,
) -> models.Experiment:
    payload = data.model_dump(exclude_unset=True)

    new_status = payload.get("status")
    new_accuracy = payload.get("accuracy", experiment.accuracy)

    # БП-3: finished требует accuracy в [0..1]
    if new_status == ExperimentStatus.FINISHED:
        if new_accuracy is None:
            raise BusinessRuleError(
                "Нельзя завершить эксперимент без указания accuracy"
            )
        if not (0.0 <= new_accuracy <= 1.0):
            raise BusinessRuleError("accuracy должен быть в диапазоне [0..1]")

    # БП-2 (на обновлении): перевести в running можно, только если других running нет
    if new_status == ExperimentStatus.RUNNING and experiment.status != ExperimentStatus.RUNNING.value:
        existing_running = db.scalar(
            select(models.Experiment).where(
                models.Experiment.model_id == experiment.model_id,
                models.Experiment.status == ExperimentStatus.RUNNING.value,
                models.Experiment.id != experiment.id,
            )
        )
        if existing_running is not None:
            raise BusinessRuleError(
                f"У модели id={experiment.model_id} уже есть running-эксперимент "
                f"id={existing_running.id}"
            )

    for field, value in payload.items():
        if value is None and field != "accuracy":
            continue
        if field == "status":
            value = value.value
        setattr(experiment, field, value)

    db.commit()
    db.refresh(experiment)
    return experiment


def delete_experiment(db: Session, experiment: models.Experiment) -> None:
    db.delete(experiment)
    db.commit()