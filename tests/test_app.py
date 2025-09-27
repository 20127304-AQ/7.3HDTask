from app import app

def test_index():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Hello from Flask TODO App!"

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

def test_todo_crud():
    client = app.test_client()
    headers = {"Authorization": "Bearer mysecrettoken"}

    # CreateTODO
    resp = client.post('/todos/', json={"task": "Write tests"}, headers=headers)
    assert resp.status_code == 201
    todo_id = resp.get_json()["id"]

    # GetTODOs
    resp = client.get('/todos/', headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1

    # UpdateTODO
    resp = client.put(f'/todos/{todo_id}', json={"task": "Write more tests"}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["task"] == "Write more tests"

    # DeleteTODO
    resp = client.delete(f'/todos/{todo_id}', headers=headers)
    assert resp.status_code == 200
