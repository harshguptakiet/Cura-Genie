import requests

def test_prometheus_metrics():
    url = "http://localhost:5000/metrics"
    resp = requests.get(url)
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text

# For ELK, check logs manually or via Kibana dashboard
