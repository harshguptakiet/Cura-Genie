import requests

def test_backend_prs_endpoint():
    url = "http://localhost:5000/api/prs/user/demo_user"
    resp = requests.get(url)
    assert resp.status_code == 200
    assert "scores" in resp.json()

def test_backend_recommendations_endpoint():
    url = "http://localhost:5000/api/recommendations"
    data = {"user_id": "demo_user"}
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    assert "recommendations" in resp.json()

def test_backend_consent_endpoint():
    url = "http://localhost:5000/api/consent/agree"
    data = {
        "user_id": "demo_user",
        "feature_id": "data_upload",
        "version": "v1",
        "user_agreement_timestamp": "2025-07-25T12:00:00Z"
    }
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
