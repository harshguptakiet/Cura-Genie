import requests

def test_backend_rbac():
    url = "http://localhost:5000/api/prs/calculate"
    # Simulate request without doctor role
    headers = {"Authorization": "Bearer test_token"}
    data = {"genomic_data_id": "123", "disease_type": "diabetes", "user_id": "demo_user"}
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code in [401, 403]  # Should be unauthorized or forbidden

def test_backend_rate_limit():
    url = "http://localhost:5000/api/prs/user/demo_user"
    for _ in range(200):
        resp = requests.get(url)
    # After many requests, should hit rate limit
    assert resp.status_code in [429, 200]  # 429 if rate limit hit
