import os

import pytest

from heapi_client import Client


@pytest.fixture(scope="session")
def base_url():
    value = os.getenv("E2E_BASE_URL")
    if not value:
        pytest.skip("Set E2E_BASE_URL to run integration tests")
    return value.rstrip("/")


@pytest.fixture(scope="session")
def live_client(base_url):
    return Client(base_url)


@pytest.fixture(scope="session")
def live_models(live_client):
    payload = live_client.discovery.list_models()
    models = payload.get("models", [])
    if not models:
        pytest.skip("No models were returned by /models")
    return models


@pytest.fixture(scope="session")
def live_model(live_models):
    wanted_model_id = os.getenv("E2E_MODEL_ID")

    if wanted_model_id:
        for model in live_models:
            if model.get("model_id") == wanted_model_id:
                return model
        pytest.skip(f"E2E_MODEL_ID='{wanted_model_id}' was not found in /models")

    return live_models[0]


@pytest.fixture(scope="session")
def live_version(live_model):
    explicit = os.getenv("E2E_MODEL_VERSION")
    if explicit:
        return explicit

    version = live_model.get("version")
    if not version:
        pytest.skip("Selected model does not expose a version")
    return version


@pytest.fixture
def live_single_input(live_model):
    inference = live_model.get("inference", {})
    input_dimension = inference.get("input_dimension")

    if not isinstance(input_dimension, int) or input_dimension < 1:
        pytest.skip("Selected model does not expose a valid inference.input_dimension")

    return [float(i + 1) / 10.0 for i in range(input_dimension)]