import pytest

from heapi_client.infer import Infer
from heapi_client.errors import SchemaValidationError


class FakeAPI:
    def __init__(self):
        self.called = False
        self.last_path = None
        self.last_json = None

    def post(self, path, json=None, data=None):
        self.called = True
        self.last_path = path
        self.last_json = json
        return {"job_id": "job-123"}


def test_submit_builds_valid_payload(tmp_path, infer_request_schema):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.request.schema.json", infer_request_schema)
    api = FakeAPI()
    infer = Infer(api, schema_path=schema_path)

    result = infer.submit(
        model_id="logistic_v1",
        version="1.0.0",
        inputs=[{"encoding": "hex", "payload": "deadbeef"}],
    )

    assert result == {"job_id": "job-123"}
    assert api.called is True
    assert api.last_path == "/infer"
    assert api.last_json == {
        "model_id": "logistic_v1",
        "version": "1.0.0",
        "inputs": [{"encoding": "hex", "payload": "deadbeef"}],
    }


def test_submit_invalid_payload_raises_before_post(tmp_path, infer_request_schema):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.request.schema.json", infer_request_schema)
    api = FakeAPI()
    infer = Infer(api, schema_path=schema_path)

    with pytest.raises(SchemaValidationError, match="schema validation"):
        infer.submit(
            model_id="logistic_v1",
            version="1.0.0",
            inputs=[{"encoding": "hex"}],
        )

    assert api.called is False