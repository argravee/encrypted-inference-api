import pytest

from heapi_client.discovery import Discovery
from heapi_client.errors import SchemaValidationError


class FakeAPI:
    def __init__(self, payload):
        self.payload = payload

    def get(self, path):
        assert path == "/models"
        return self.payload


def test_list_models_returns_valid_payload(tmp_path, get_models_schema, get_models_response):
    from conftest import write_json

    schema_path = write_json(tmp_path, "get_models.response.schema.json", get_models_schema)
    discovery = Discovery(FakeAPI(get_models_response), schema_path=schema_path)

    payload = discovery.list_models()
    assert payload["api_version"] == "1.0.0"
    assert payload["models"][0]["model_id"] == "logistic_v1"


def test_get_model_returns_matching_model(tmp_path, get_models_schema, get_models_response):
    from conftest import write_json

    schema_path = write_json(tmp_path, "get_models.response.schema.json", get_models_schema)
    discovery = Discovery(FakeAPI(get_models_response), schema_path=schema_path)

    model = discovery.get_model("logistic_v1")
    assert model["version"] == "1.0.0"


def test_get_model_missing_raises_value_error(tmp_path, get_models_schema, get_models_response):
    from conftest import write_json

    schema_path = write_json(tmp_path, "get_models.response.schema.json", get_models_schema)
    discovery = Discovery(FakeAPI(get_models_response), schema_path=schema_path)

    with pytest.raises(ValueError, match="not found"):
        discovery.get_model("missing_model")


def test_list_models_invalid_payload_raises_schema_validation_error(
        tmp_path, get_models_schema
):
    from conftest import write_json

    bad_payload = {"models": "not-an-array"}
    schema_path = write_json(tmp_path, "get_models.response.schema.json", get_models_schema)
    discovery = Discovery(FakeAPI(bad_payload), schema_path=schema_path)

    with pytest.raises(SchemaValidationError, match="schema validation"):
        discovery.list_models()


def test_load_schema_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Discovery(FakeAPI({}), schema_path=tmp_path / "missing.json")