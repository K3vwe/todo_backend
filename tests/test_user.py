payload ={
        "fullname": "John Doe",
        "username": "jonnydoe",
        "email": "johndoe@gmail.com",
        "hashed_password": "onosnonso#$*@Ynsdf"
    }

# -----------------------------
# TEST CREATE USER
# -----------------------------
def test_create_user(client):

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
        json=payload
    )

    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.get(f'/api/v1/users/{user_id}')
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == payload["username"]
    assert data["fullname"] == payload["fullname"]
    assert data["email"] == payload["email"]
   



# -----------------------------
# TEST UPDATE USER BY ID
# -----------------------------
def test_update_user(client):
    # Step 1: Create user
    create = client.post(
        "/api/v1/users/",
        json=payload
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
    assert data["fullname"] == update_payload["fullname"]
    assert data["username"] == update_payload["username"]
    assert data["email"] == payload["email"]  # unchanged
    assert "updated_at" in data


# -----------------------------
# TEST DELETE USER BY ID
# -----------------------------
def test_delete_user(client):
    # Step 1: Create user
    create = client.post(
        "/api/v1/users/",
        json=payload
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

