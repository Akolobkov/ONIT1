def _create_task(client, title="task"):
    r = client.post("/tasks", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def _create_model(client, task_id, name="model"):
    r = client.post(
        "/models",
        json={"name": name, "framework": "pytorch", "task_id": task_id},
    )
    assert r.status_code == 201, r.text
    return r.json()


def _create_experiment(client, model_id, name="exp", status="running", accuracy=None):
    body = {"name": name, "status": status, "model_id": model_id}
    if accuracy is not None:
        body["accuracy"] = accuracy
    return client.post("/experiments", json=body)


def test_full_chain_task_model_experiment(client):
    task = _create_task(client, "chain-task")
    model = _create_model(client, task["id"], "chain-model")

    r = _create_experiment(client, model["id"], name="chain-exp", status="running")
    assert r.status_code == 201, r.text
    exp = r.json()

    r = client.get(f"/experiments/{exp['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

    r = client.get(f"/tasks/{task['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "open"


def test_conflict_on_second_running_experiment(client):
    task = _create_task(client, "conflict-task")
    model = _create_model(client, task["id"], "conflict-model")

    r1 = _create_experiment(client, model["id"], name="e1", status="running")
    assert r1.status_code == 201

    r2 = _create_experiment(client, model["id"], name="e2", status="running")
    assert r2.status_code == 409
    assert "running" in r2.json()["detail"]



def test_delete_task_cascades(client):
    task = _create_task(client, "cascade-task")
    model = _create_model(client, task["id"], "cascade-model")
    exp = _create_experiment(
        client, model["id"], name="cascade-exp", status="finished", accuracy=0.5
    )
    assert exp.status_code == 201
    exp_id = exp.json()["id"]

    r = client.delete(f"/tasks/{task['id']}")
    assert r.status_code == 204

    assert client.get(f"/tasks/{task['id']}").status_code == 404
    assert client.get(f"/models/{model['id']}").status_code == 404
    assert client.get(f"/experiments/{exp_id}").status_code == 404