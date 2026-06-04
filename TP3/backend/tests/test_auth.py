def test_register_creates_user(client):
    res = client.post("/api/auth/register", json={"email": "test@example.com", "password": "secret"})
    assert res.status_code == 201
    assert res.json()["email"] == "test@example.com"

def test_register_duplicate_email_fails(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "secret"})
    res = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "secret"})
    assert res.status_code == 409

def test_login_returns_token(client):
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "secret"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"

def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "correct"})
    res = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert res.status_code == 401
