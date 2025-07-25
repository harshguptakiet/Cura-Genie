import requests

def test_cancer_xgb_predict():
    url = "http://localhost:8000/predict"
    data = {"features": [0.1, 0.2, 0.3, 0.4, 0.5]}
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    assert "risk_score" in resp.json()

def test_cancer_seq_tf_predict():
    url = "http://localhost:8001/predict_seq"
    data = {"features": [0.1]*1000}
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    assert "risk_score" in resp.json()
