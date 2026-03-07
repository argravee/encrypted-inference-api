import pytest

from heapi_client.client import Client
from heapi_client.errors import SchemaValidationError


class DummySession:
    def __init__(self):
        self.encrypted = []

    def encrypt(self, values):
        self.encrypted.append(values)
        return {"encoding": "hex", "payload": "deadbeef"}

    def decrypt(self, response):
        return [0.99]


@pytest.fixture
def client():
    return Client("http://localhost:8000")


def test_infer_single_vector_happy_path(monkeypatch, client, model_metadata):
    dummy_session = DummySession()

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)
    monkeypatch.setattr(
        "heapi_client.client.CKKS_Session.from_model",
        lambda model: dummy_session,
    )

    submitted = {}

    def fake_submit(model_id, version, inputs):
        submitted["model_id"] = model_id
        submitted["version"] = version
        submitted["inputs"] = inputs
        return {"job_id": "job-123"}

    monkeypatch.setattr(client.infer_api, "submit", fake_submit)
    monkeypatch.setattr(
        client.jobs,
        "wait",
        lambda job_id: {
            "model_id": "logistic_v1",
            "version": "1.0.0",
            "payload": "beadfeed",
        },
    )

    result = client.infer(
        model_id="logistic_v1",
        values=[1, 2, 3, 4, 5, 6, 7, 8],
    )

    assert result == [0.99]
    assert submitted["model_id"] == "logistic_v1"
    assert submitted["version"] == "1.0.0"
    assert submitted["inputs"] == [{"encoding": "hex", "payload": "deadbeef"}]
    assert dummy_session.encrypted == [[1, 2, 3, 4, 5, 6, 7, 8]]


def test_infer_batch_happy_path(monkeypatch, client, model_metadata):
    dummy_session = DummySession()

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)
    monkeypatch.setattr(
        "heapi_client.client.CKKS_Session.from_model",
        lambda model: dummy_session,
    )
    monkeypatch.setattr(
        client.infer_api,
        "submit",
        lambda model_id, version, inputs: {"job_id": "job-123"},
    )
    monkeypatch.setattr(
        client.jobs,
        "wait",
        lambda job_id: {
            "model_id": "logistic_v1",
            "version": "1.0.0",
            "payload": "beadfeed",
        },
    )

    batch = [
        [1, 2, 3, 4, 5, 6, 7, 8],
        [8, 7, 6, 5, 4, 3, 2, 1],
    ]

    result = client.infer(
        model_id="logistic_v1",
        values=batch,
    )

    assert result == [0.99]
    assert dummy_session.encrypted == batch


def test_rejects_wrong_input_dimension_before_submit(monkeypatch, client, model_metadata):
    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)

    submit_called = {"value": False}

    def fake_submit(*args, **kwargs):
        submit_called["value"] = True
        return {"job_id": "job-123"}

    monkeypatch.setattr(client.infer_api, "submit", fake_submit)

    with pytest.raises(SchemaValidationError, match="expected 8"):
        client.infer(
            model_id="logistic_v1",
            values=[1, 2, 3],
        )

    assert submit_called["value"] is False


def test_rejects_batch_larger_than_max_batch_size(monkeypatch, client, model_metadata):
    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)

    oversized_batch = [[1, 2, 3, 4, 5, 6, 7, 8] for _ in range(17)]

    with pytest.raises(SchemaValidationError, match="exceeds model max_batch_size 16"):
        client.infer(
            model_id="logistic_v1",
            values=oversized_batch,
        )


def test_rejects_non_numeric_single_vector(monkeypatch, client, model_metadata):
    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)

    with pytest.raises(SchemaValidationError, match="numeric values"):
        client.infer(
            model_id="logistic_v1",
            values=[1, 2, "x", 4, 5, 6, 7, 8],
        )


def test_rejects_non_numeric_batch_vector(monkeypatch, client, model_metadata):
    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)

    with pytest.raises(SchemaValidationError, match="numeric values"):
        client.infer(
            model_id="logistic_v1",
            values=[
                [1, 2, 3, 4, 5, 6, 7, 8],
                [8, 7, 6, 5, "bad", 3, 2, 1],
            ],
        )


def test_rejects_empty_values(monkeypatch, client, model_metadata):
    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)

    with pytest.raises(SchemaValidationError, match="non-empty list"):
        client.infer(
            model_id="logistic_v1",
            values=[],
        )


def test_rejects_missing_input_dimension(monkeypatch, client, model_metadata):
    broken_model = dict(model_metadata)
    broken_model["inference"] = {"output_dimension": 1}

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: broken_model)

    with pytest.raises(SchemaValidationError, match="missing inference.input_dimension"):
        client.infer(
            model_id="logistic_v1",
            values=[1, 2, 3, 4, 5, 6, 7, 8],
        )


def test_rejects_invalid_max_batch_size_metadata(monkeypatch, client, model_metadata):
    broken_model = dict(model_metadata)
    broken_model["constraints"] = {"max_batch_size": 0}

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: broken_model)

    with pytest.raises(SchemaValidationError, match="max_batch_size must be a positive integer"):
        client.infer(
            model_id="logistic_v1",
            values=[1, 2, 3, 4, 5, 6, 7, 8],
        )


def test_rejects_missing_version_when_not_provided(monkeypatch, client, model_metadata):
    broken_model = dict(model_metadata)
    broken_model["version"] = ""

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: broken_model)

    with pytest.raises(SchemaValidationError, match="missing a usable version field"):
        client.infer(
            model_id="logistic_v1",
            values=[1, 2, 3, 4, 5, 6, 7, 8],
        )


def test_explicit_version_overrides_model_version(monkeypatch, client, model_metadata):
    dummy_session = DummySession()

    monkeypatch.setattr(client.discovery, "get_model", lambda model_id: model_metadata)
    monkeypatch.setattr(
        "heapi_client.client.CKKS_Session.from_model",
        lambda model: dummy_session,
    )

    submitted = {}

    def fake_submit(model_id, version, inputs):
        submitted["version"] = version
        return {"job_id": "job-123"}

    monkeypatch.setattr(client.infer_api, "submit", fake_submit)
    monkeypatch.setattr(
        client.jobs,
        "wait",
        lambda job_id: {
            "model_id": "logistic_v1",
            "version": "1.0.0",
            "payload": "beadfeed",
        },
    )

    client.infer(
        model_id="logistic_v1",
        values=[1, 2, 3, 4, 5, 6, 7, 8],
        version="2.0.0",
    )

    assert submitted["version"] == "2.0.0"