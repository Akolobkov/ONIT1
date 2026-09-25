from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import BusinessRuleError
from app.models import ExperimentStatus, TaskStatus


# ---------- Task ----------

def get_tasks(db: Session, status: TaskStatus | None = None) -> list[models.Task]:
    stmt = select(models.Task)
    if status is not None:
        stmt = stmt.where(models.Task.status == status.value)
    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.get(models.Task, task_id)


def create_task(db: Session, data: schemas.TaskCreate) -> models.Task:
    task = models.Task(
        title=data.title,
        description=data.description,
        status=data.status.value,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: models.Task, data: schemas.TaskUpdate) -> models.Task:
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


# ---------- Model ----------

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


def create_model(db: Session, data: schemas.ModelCreate) -> models.Model:
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


def update_model(db: Session, model: models.Model, data: schemas.ModelUpdate) -> models.Model:
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


# ---------- Experiment ----------

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


def create_experiment(db: Session, data: schemas.ExperimentCreate) -> models.Experiment:
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
    data: schemas.ExperimentUpdate,
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