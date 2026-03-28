from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from server.app.main import app
from server.core.jobs.queue import reset_jobs


@pytest.fixture
def api_client(monkeypatch, sample_model_definition):
    import server.app.routes.models as models_route
    import server.app.routes.infer as infer_route

    registry = {
        (sample_model_definition.model_id, sample_model_definition.version): sample_model_definition
    }

    monkeypatch.setattr(models_route, "MODEL_REGISTRY", registry)
    monkeypatch.setattr(infer_route, "MODEL_REGISTRY", registry)

    monkeypatch.setattr(
        infer_route,
        "validate_ciphertext_structure",
        lambda **kwargs: {"validated": True},
    )

    app.dependency_overrides.clear()
    app.dependency_overrides[infer_route.get_crypto_backend] = lambda: object()
    reset_jobs()

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
    reset_jobs()