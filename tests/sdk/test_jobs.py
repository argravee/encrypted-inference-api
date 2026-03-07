import pytest

from heapi_client.errors import JobFailedError, JobTimeoutError, SchemaValidationError
from heapi_client.jobs import Jobs


class FakeAPI:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, path):
        self.calls += 1
        return self.responses.pop(0)


def test_wait_returns_direct_final_response(tmp_path, infer_response_schema, infer_response_payload):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    api = FakeAPI([infer_response_payload])
    jobs = Jobs(api, schema_path=schema_path)

    result = jobs.wait("job-1", interval=0, timeout=1)
    assert result == infer_response_payload
    assert api.calls == 1


def test_wait_returns_wrapped_completed_response(tmp_path, infer_response_schema, infer_response_payload):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    wrapped = {
        "status": "completed",
        "result": infer_response_payload,
    }
    api = FakeAPI([wrapped])
    jobs = Jobs(api, schema_path=schema_path)

    result = jobs.wait("job-1", interval=0, timeout=1)
    assert result == infer_response_payload


def test_wait_raises_on_failed_job(tmp_path, infer_response_schema):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    api = FakeAPI([{"status": "failed", "error": "bad things"}])
    jobs = Jobs(api, schema_path=schema_path)

    with pytest.raises(JobFailedError, match="bad things"):
        jobs.wait("job-1", interval=0, timeout=1)


def test_wait_times_out_on_queued_job(tmp_path, infer_response_schema, monkeypatch):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    api = FakeAPI([{"status": "queued"}, {"status": "queued"}, {"status": "queued"}])
    jobs = Jobs(api, schema_path=schema_path)

    times = iter([0.0, 0.6, 1.2])
    monkeypatch.setattr("heapi_client.jobs.time.time", lambda: next(times))
    monkeypatch.setattr("heapi_client.jobs.time.sleep", lambda _: None)

    with pytest.raises(JobTimeoutError, match="exceeded timeout"):
        jobs.wait("job-1", interval=0, timeout=1.0)


def test_wait_unknown_status_raises_schema_validation_error(
        tmp_path, infer_response_schema
):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    api = FakeAPI([{"status": "mystery"}])
    jobs = Jobs(api, schema_path=schema_path)

    with pytest.raises(SchemaValidationError, match="Unknown job status"):
        jobs.wait("job-1", interval=0, timeout=1)


def test_wait_completed_with_invalid_final_payload_raises_schema_validation_error(
        tmp_path, infer_response_schema
):
    from conftest import write_json

    schema_path = write_json(tmp_path, "infer.response.schema.json", infer_response_schema)
    bad_wrapped = {
        "status": "completed",
        "result": {"model_id": "x", "version": "1.0.0"},
    }
    api = FakeAPI([bad_wrapped])
    jobs = Jobs(api, schema_path=schema_path)

    with pytest.raises(SchemaValidationError, match="Final inference response failed schema validation"):
        jobs.wait("job-1", interval=0, timeout=1)