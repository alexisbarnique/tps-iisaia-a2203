import pytest


@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/register", json={"email": "goals@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "goals@example.com", "password": "secret"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_create_goal_ok(client, auth_headers):
    res = client.post("/api/goals", json={"year": 2026, "category": "book", "target": 12}, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["year"] == 2026
    assert data["category"] == "book"
    assert data["target"] == 12
    assert "id" in data


def test_list_goals_returns_progress(client, auth_headers):
    client.post(
        "/api/entries",
        json={"category": "book", "title": "1984", "date": "2026-03-01"},
        headers=auth_headers,
    )
    client.post("/api/goals", json={"year": 2026, "category": "book", "target": 5}, headers=auth_headers)
    res = client.get("/api/goals", headers=auth_headers)
    assert res.status_code == 200
    goals = res.json()
    assert len(goals) == 1
    assert goals[0]["current"] == 1
    assert goals[0]["percentage"] == 20.0


def test_update_goal_ok(client, auth_headers):
    res = client.post(
        "/api/goals", json={"year": 2026, "category": "movie_series", "target": 20}, headers=auth_headers
    )
    goal_id = res.json()["id"]
    res = client.put(f"/api/goals/{goal_id}", json={"target": 30}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["target"] == 30


def test_delete_goal_ok(client, auth_headers):
    res = client.post(
        "/api/goals", json={"year": 2026, "category": "event", "target": 10}, headers=auth_headers
    )
    goal_id = res.json()["id"]
    assert client.delete(f"/api/goals/{goal_id}", headers=auth_headers).status_code == 204
    remaining = client.get("/api/goals", headers=auth_headers).json()
    assert all(g["id"] != goal_id for g in remaining)


def test_create_goal_duplicate_returns_409(client, auth_headers):
    client.post("/api/goals", json={"year": 2026, "category": "book", "target": 12}, headers=auth_headers)
    res = client.post("/api/goals", json={"year": 2026, "category": "book", "target": 5}, headers=auth_headers)
    assert res.status_code == 409


def test_update_goal_other_user_returns_404(client):
    for email in ("goals_a@example.com", "goals_b@example.com"):
        client.post("/api/auth/register", json={"email": email, "password": "secret"})
    h_a = {"Authorization": f"Bearer {client.post('/api/auth/login', json={'email': 'goals_a@example.com', 'password': 'secret'}).json()['access_token']}"}
    h_b = {"Authorization": f"Bearer {client.post('/api/auth/login', json={'email': 'goals_b@example.com', 'password': 'secret'}).json()['access_token']}"}
    goal_id = client.post("/api/goals", json={"year": 2026, "category": "book", "target": 12}, headers=h_a).json()["id"]
    assert client.put(f"/api/goals/{goal_id}", json={"target": 99}, headers=h_b).status_code == 404


def test_delete_goal_other_user_returns_404(client):
    for email in ("goals_c@example.com", "goals_d@example.com"):
        client.post("/api/auth/register", json={"email": email, "password": "secret"})
    h_c = {"Authorization": f"Bearer {client.post('/api/auth/login', json={'email': 'goals_c@example.com', 'password': 'secret'}).json()['access_token']}"}
    h_d = {"Authorization": f"Bearer {client.post('/api/auth/login', json={'email': 'goals_d@example.com', 'password': 'secret'}).json()['access_token']}"}
    goal_id = client.post("/api/goals", json={"year": 2026, "category": "city", "target": 3}, headers=h_c).json()["id"]
    assert client.delete(f"/api/goals/{goal_id}", headers=h_d).status_code == 404


def test_create_goal_unauthenticated_returns_403(client):
    res = client.post("/api/goals", json={"year": 2026, "category": "book", "target": 12})
    assert res.status_code == 403
