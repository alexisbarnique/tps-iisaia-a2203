import pytest

@pytest.fixture()
def auth_headers_with_data(client):
    client.post("/api/auth/register", json={"email": "summary@example.com", "password": "secret"})
    res = client.post("/api/auth/login", json={"email": "summary@example.com", "password": "secret"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # seed entries in March 2025
    client.post("/api/entries", json={"category": "book", "title": "Dune", "date": "2025-03-05"}, headers=headers)
    client.post("/api/entries", json={"category": "book", "title": "1984", "date": "2025-03-20"}, headers=headers)
    client.post("/api/entries", json={"category": "city", "title": "Madrid", "date": "2025-03-10", "country": "España"}, headers=headers)
    client.post("/api/entries", json={"category": "city", "title": "Barcelona", "date": "2025-03-12", "country": "España"}, headers=headers)
    return headers

def test_monthly_summary_returns_only_categories_with_entries(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2025/3", headers=auth_headers_with_data)
    assert res.status_code == 200
    data = res.json()
    assert data["year"] == 2025
    assert data["month"] == 3
    categories = [h["category"] for h in data["highlights"]]
    assert "book" in categories
    assert "city" in categories
    assert "event" not in categories  # no events registered

def test_monthly_summary_empty_period_returns_empty_highlights(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2024/1", headers=auth_headers_with_data)
    assert res.status_code == 200
    assert res.json()["highlights"] == []

def test_monthly_city_summary_counts_countries(client, auth_headers_with_data):
    res = client.get("/api/summaries/monthly/2025/3", headers=auth_headers_with_data)
    city_highlight = next(h for h in res.json()["highlights"] if h["category"] == "city")
    assert city_highlight["countries"] == 1
    assert city_highlight["cities"] == 2

def test_annual_summary_groups_by_month(client, auth_headers_with_data):
    res = client.get("/api/summaries/annual/2025", headers=auth_headers_with_data)
    assert res.status_code == 200
    data = res.json()
    assert data["year"] == 2025
    assert len(data["months"]) >= 1
    assert data["months"][0]["month"] == 3

def test_annual_totals_count_all_entries(client, auth_headers_with_data):
    res = client.get("/api/summaries/annual/2025", headers=auth_headers_with_data)
    totals = res.json()["totals"]
    assert totals.get("book") == 2
    assert totals.get("city") == 2
