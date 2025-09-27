from app import app

def test_index():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Hello from Flask!"

def test_health():
    client = app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"

def test_metrics():
    client = app.test_client()
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert b"http_requests_total" in resp.data
