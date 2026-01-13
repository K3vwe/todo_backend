# -----------------------------
# TEST CREATE USER
# -----------------------------
def test_create_user(client):
    payload ={
        "fullname": "John Doe",
        "username": "jonnydoe",
        "email": "johndoe@gmail.com",
        "hashed_password": "onosnonso#$*@Ynsdf"
    }

    response = client.post('/api/v1/users/', json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["fullname"] == payload["fullname"]
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data

# -----------------------------
# TEST GET USER BY ID
# -----------------------------
def test_get_user_by_id(client):
    create = client.post(
        '/api/v1/users/',
        json={
            "fullname": "Fuled",
            "username": "active",
            "email": "fuled@gmail.com",
            "hashed_password": "securehash"
        }
    )

    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.get(f'/api/v1/users/{user_id}')
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "active"


# -----------------------------
# TEST UPDATE USER BY ID
# -----------------------------
def test_update_user(client):
    # Step 1: Create user
    create = client.post(
        "/api/v1/users/",
        json={
            "fullname": "John Doe",
            "username": "johndoe",
            "email": "john@gmail.com",
            "hashed_password": "hash123"
        }
    )

    user_id = create.json()["id"]

    # Step 2: Update user (PATCH)
    update_payload = {
        "fullname": "John Updated",
        "username": "johnny"
    }

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json=update_payload
    )

    # assert response.status_code == 200
    data = response.json()

    # Step 3: Assertions
    assert data["id"] == user_id
    assert data["fullname"] == "John Updated"
    assert data["username"] == "johnny"
    assert data["email"] == "john@gmail.com"  # unchanged
    assert "updated_at" in data


# -----------------------------
# TEST DELETE USER BY ID
# -----------------------------
def test_delete_user(client):
    # Step 1: Create user
    create = client.post(
        "/api/v1/users/",
        json={
            "fullname": "Jane Doe",
            "username": "janedoe",
            "email": "jane@gmail.com",
            "hashed_password": "hash123"
        }
    )

    # assert create.status_code == 200
    user_id = create.json()["id"]

    # Step 2: Delete user
    response = client.delete(f"/api/v1/users/{user_id}")
    # assert response.status_code == 200

    data = response.json()
    assert data["User_id"] == user_id

    # Step 3: Verify user is gone
    get_deleted = client.get(f"/api/v1/users/{user_id}")
    assert get_deleted.status_code == 404
