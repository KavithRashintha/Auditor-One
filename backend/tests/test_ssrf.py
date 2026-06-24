import pytest
from fastapi.testclient import TestClient

def test_ssrf_rejection(client: TestClient):
    # Test 1: Cloud metadata IP (169.254.169.254)
    payload_metadata = {"url": "http://169.254.169.254/latest/meta-data/"}
    # Since the SSE endpoint yields an event: error, the HTTP response itself will be 200 OK
    # We must read the SSE stream and verify the error event is emitted.
    
    with client.stream("POST", "/api/v1/audit", json=payload_metadata) as response:
        assert response.status_code == 200
        content = response.read().decode("utf-8")
        assert "event: error" in content
        assert '"stage": "SSRF"' in content
        assert "Invalid target destination" in content

    # Test 2: Localhost
    payload_localhost = {"url": "http://localhost:8000"}
    with client.stream("POST", "/api/v1/audit", json=payload_localhost) as response:
        assert response.status_code == 200
        content = response.read().decode("utf-8")
        assert "event: error" in content
        assert '"stage": "SSRF"' in content
        assert "Invalid target destination" in content
