# -----------------------------
# TEST CREATE TASK POST
# -----------------------------
def test_create_task(client):
    payload = {
        "title": "Give Thanks",
        "description": "Thank God",
        "priority": "MEDIUM",
        "due_at": "2026-01-15T12:00:00"
    }

    response = client.post("/api/v1/tasks/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == payload["priority"]
    assert data["status"] == "PENDING"
    assert "id" in data


# -----------------------------
# TEST GET ALL TASKS
# -----------------------------
def test_get_tasks(client):
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# -----------------------------
# TEST GET TASK BY ID
# -----------------------------
def test_get_task_by_id(client):
    create = client.post(
        "/api/v1/tasks/",
        json={"title": "Smile more often", "priority": "low"}
    )

    task_id = create.json()["id"]
    response = client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


# -----------------------------
# TEST UPDATE TASK BY ID
# -----------------------------
def test_update_task_by_id(client):
    create = client.post(
        "/api/v1/tasks/",
        json={"title": "Old Task", "priority": "low"}
    )

    task_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "New Task", "status": "COMPLETED"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Task"
    assert response.json()["status"] == "COMPLETED"


# -----------------------------
# TEST DELETE TASK BY ID
# -----------------------------
def test_delete_task(client):
    create = client.post(
        "/api/v1/tasks/",
        json={"title": "To be deleted", "priority": "medium"}
    )

    task_id = create.json()["id"]
    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200

    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404