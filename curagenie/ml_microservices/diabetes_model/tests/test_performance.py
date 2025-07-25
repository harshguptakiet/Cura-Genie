import requests
import time

def test_diabetes_xgb_performance():
    url = "http://localhost:8000/predict"
    data = {"features": [0.1, 0.2, 0.3, 0.4, 0.5]}
    start = time.time()
    resp = requests.post(url, json=data)
    duration = time.time() - start
    assert resp.status_code == 200
    assert duration < 1.0  # Expect <1s inference

# Repeat for other services as needed
