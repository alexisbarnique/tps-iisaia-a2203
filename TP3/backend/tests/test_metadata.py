def test_categories_returns_all_five(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    values = [c["value"] for c in res.json()]
    assert set(values) == {"event", "movie_series", "book", "city", "place"}

def test_place_types_returns_six(client):
    res = client.get("/api/place-types")
    assert res.status_code == 200
    values = [p["value"] for p in res.json()]
    assert set(values) == {"restaurant", "cafe", "museum", "bar", "park", "other"}
