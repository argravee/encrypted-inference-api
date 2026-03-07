import pytest
from requests.exceptions import RequestException, Timeout

from heapi_client.api import API
from heapi_client.errors import APIError, ConnectionError


class DummyResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload or {}
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_get_success_returns_json(monkeypatch):
    def fake_get(url, timeout):
        assert url == "http://localhost:8000/models"
        assert timeout == 5.0
        return DummyResponse({"ok": True})

    monkeypatch.setattr("heapi_client.api.requests.get", fake_get)

    api = API("http://localhost:8000")
    assert api.get("/models") == {"ok": True}


def test_get_timeout_raises_connection_error(monkeypatch):
    def fake_get(url, timeout):
        raise Timeout("boom")

    monkeypatch.setattr("heapi_client.api.requests.get", fake_get)

    api = API("http://localhost:8000")

    with pytest.raises(ConnectionError, match="timed out"):
        api.get("/models")


def test_get_request_exception_raises_api_error(monkeypatch):
    response = DummyResponse({"error": "bad"}, status_code=500)

    def fake_get(url, timeout):
        exc = RequestException("boom")
        exc.response = response
        raise exc

    monkeypatch.setattr("heapi_client.api.requests.get", fake_get)

    api = API("http://localhost:8000")

    with pytest.raises(APIError) as excinfo:
        api.get("/models")

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error": "bad"}


def test_post_success_returns_json(monkeypatch):
    def fake_post(url, data, json, timeout):
        assert url == "http://localhost:8000/infer"
        assert json == {"x": 1}
        return DummyResponse({"job_id": "123"})

    monkeypatch.setattr("heapi_client.api.requests.post", fake_post)

    api = API("http://localhost:8000")
    assert api.post("/infer", json={"x": 1}) == {"job_id": "123"}


def test_post_timeout_raises_connection_error(monkeypatch):
    def fake_post(url, data, json, timeout):
        raise Timeout("boom")

    monkeypatch.setattr("heapi_client.api.requests.post", fake_post)

    api = API("http://localhost:8000")

    with pytest.raises(ConnectionError, match="timed out"):
        api.post("/infer", json={"x": 1})


def test_post_request_exception_raises_api_error(monkeypatch):
    response = DummyResponse({"error": "bad"}, status_code=400)

    def fake_post(url, data, json, timeout):
        exc = RequestException("boom")
        exc.response = response
        raise exc

    monkeypatch.setattr("heapi_client.api.requests.post", fake_post)

    api = API("http://localhost:8000")

    with pytest.raises(APIError) as excinfo:
        api.post("/infer", json={"x": 1})

    assert excinfo.value.status_code == 400
    assert excinfo.value.details == {"error": "bad"}