import requests

def test_frontend_health_check():
    url = "http://localhost:3000/api/health"
    resp = requests.get(url)
    assert resp.status_code == 200
    assert "status" in resp.json()

# Add more frontend integration tests as needed
