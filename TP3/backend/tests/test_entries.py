import pytest

@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/register", json={"email": "entries@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "entries@example.com", "password": "secret"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_event_entry(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "event", "title": "Coldplay", "date": "2025-03-15"
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["title"] == "Coldplay"

def test_create_book_with_saga(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "book", "title": "El nombre del viento",
        "date": "2025-03-10", "saga_name": "Crónica del Asesino de Reyes", "saga_part": 1, "rating": 5
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json()["saga_name"] == "Crónica del Asesino de Reyes"

def test_create_city_entry(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "city", "title": "París", "date": "2025-07-01", "country": "Francia"
    }, headers=auth_headers)
    assert res.status_code == 201

def test_invalid_category_field_rejected(client, auth_headers):
    res = client.post("/api/entries", json={
        "category": "event", "title": "Concert", "date": "2025-01-01", "rating": 5
    }, headers=auth_headers)
    assert res.status_code == 422

def test_list_entries_returns_only_own(client, auth_headers):
    client.post("/api/entries", json={"category": "event", "title": "Show", "date": "2025-01-01"}, headers=auth_headers)
    res = client.get("/api/entries", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

def test_delete_entry(client, auth_headers):
    res = client.post("/api/entries", json={"category": "event", "title": "ToDelete", "date": "2025-01-01"}, headers=auth_headers)
    entry_id = res.json()["id"]
    del_res = client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_update_entry(client, auth_headers):
    res = client.post("/api/entries", json={"category": "event", "title": "Original", "date": "2025-01-01"}, headers=auth_headers)
    entry_id = res.json()["id"]
    put_res = client.put(f"/api/entries/{entry_id}", json={
        "category": "event", "title": "Updated", "date": "2025-01-01"
    }, headers=auth_headers)
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Updated"

def test_unauthenticated_request_rejected(client):
    res = client.get("/api/entries")
    assert res.status_code == 403
