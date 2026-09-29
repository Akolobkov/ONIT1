import pytest

from app import crud, schemas
from app.exceptions import BusinessRuleError
from app.models import ExperimentStatus, Framework, TaskStatus


def _make_task(db, title="task-1", status=TaskStatus.OPEN):
    return crud.task_controllers.create_task(db, schemas.task_schema.TaskCreate(title=title, status=status))


def _make_model(db, task_id, name="model-1", framework=Framework.PYTORCH):
    return crud.model_controllers.create_model(
        db, schemas.model_schema.ModelCreate(name=name, framework=framework, task_id=task_id)
    )


def _make_experiment(
    db, model_id, name="exp-1", status=ExperimentStatus.RUNNING, accuracy=None
):
    return crud.experiment_controllers.create_experiment(
        db,
        schemas.experiment_schema.ExperimentCreate(
            name=name, status=status, accuracy=accuracy, model_id=model_id
        ),
    )

def test_cannot_add_model_to_done_task(db_session):
    task = _make_task(db_session, title="t1", status=TaskStatus.DONE)
    with pytest.raises(BusinessRuleError) as exc:
        _make_model(db_session, task.id, name="m1")
    assert "done" in str(exc.value)


def test_two_running_experiments_forbidden(db_session):
    task = _make_task(db_session)
    model = _make_model(db_session, task.id)
    _make_experiment(db_session, model.id, name="e1", status=ExperimentStatus.RUNNING)

    with pytest.raises(BusinessRuleError) as exc:
        _make_experiment(
            db_session, model.id, name="e2", status=ExperimentStatus.RUNNING
        )
    assert "running" in str(exc.value)



def test_finish_without_accuracy_forbidden(db_session):
    task = _make_task(db_session)
    model = _make_model(db_session, task.id)
    exp = _make_experiment(db_session, model.id, status=ExperimentStatus.RUNNING)

    with pytest.raises(BusinessRuleError) as exc:
        crud.experiment_controllers.update_experiment(
            db_session,
            exp,
            schemas.experiment_schema.ExperimentUpdate(status=ExperimentStatus.FINISHED),
        )
    assert "accuracy" in str(exc.value)


def test_cannot_delete_task_with_running_experiment(db_session):
    task = _make_task(db_session)
    model = _make_model(db_session, task.id)
    _make_experiment(db_session, model.id, status=ExperimentStatus.RUNNING)

    with pytest.raises(BusinessRuleError) as exc:
        crud.task_controllers.delete_task(db_session, task)
    assert "running" in str(exc.value)


def test_bp5_done_requires_finished_experiment(db_session):
    task = _make_task(db_session)
    model = _make_model(db_session, task.id)
    _make_experiment(db_session, model.id, status=ExperimentStatus.RUNNING)

    with pytest.raises(BusinessRuleError) as exc:
        crud.task_controllers.update_task(
            db_session, task, schemas.task_schema.TaskUpdate(status=TaskStatus.DONE)
        )
    msg = str(exc.value).lower()
    assert "заверш" in msg or "finished" in msg



def test_create_task_and_model_and_experiment(db_session):
    task = _make_task(db_session, title="ok-task")
    model = _make_model(db_session, task.id, name="ok-model")
    exp = _make_experiment(
        db_session,
        model.id,
        name="ok-exp",
        status=ExperimentStatus.FINISHED,
        accuracy=0.9,
    )
    assert task.id and model.id and exp.id
    assert exp.accuracy == 0.9