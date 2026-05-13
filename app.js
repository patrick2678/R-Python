def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def register_user(client, username="user1", email="user1@example.com", password="123"):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(client, email="user1@example.com", password="123"):
    return client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


def get_token(client, username="user1", email="user1@example.com", password="123"):
    register_user(client, username=username, email=email, password=password)
    response = login_user(client, email=email, password=password)
    assert response.status_code == 200, response.json()
    return response.json()["access_token"]


def admin_token(client):
    response = login_user(client, email="admin@blog.com", password="123")
    assert response.status_code == 200, response.json()
    return response.json()["access_token"]


def promote_user(client, email: str, role: str):
    token = admin_token(client)
    users_response = client.get("/users/", headers=auth_headers(token))
    assert users_response.status_code == 200, users_response.json()

    user = next(item for item in users_response.json() if item["email"] == email)
    response = client.put(
        f"/users/{user['id']}/role",
        json={"role": role},
        headers=auth_headers(token),
    )
    assert response.status_code == 200, response.json()
    return response.json()


def author_token(client, username="author1", email="author@example.com", password="123"):
    token = get_token(client, username=username, email=email, password=password)
    promote_user(client, email=email, role="author")
    return token


def create_post(client, token, title="Post Title", content="This is valid post content."):
    response = client.post(
        "/posts/",
        json={"title": title, "content": content},
        headers=auth_headers(token),
    )
    assert response.status_code == 201, response.json()
    return response.json()
