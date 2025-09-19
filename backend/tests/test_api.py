from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    from importlib import reload
    import app.core.config as config_module

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        db_path = tmp_path / "test.db"
        storage_path = tmp_path / "storage"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"  # noqa: S105
        os.environ["STORAGE_DIR"] = str(storage_path)
        os.environ["SECRET_KEY"] = "test-secret"  # noqa: S105

        # Clear cached settings to pick up new environment variables
        config_module.get_settings.cache_clear()  # type: ignore[attr-defined]
        reload(config_module)
        from app.main import app

        with TestClient(app) as test_client:
            yield test_client

    # reset cache after tests
    get_settings.cache_clear()
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("STORAGE_DIR", None)
    os.environ.pop("SECRET_KEY", None)


def test_signup_login_and_project_flow(client: TestClient) -> None:
    signup_response = client.post(
        "/auth/signup",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert signup_response.status_code == 201, signup_response.text

    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    voices_response = client.get("/voices", headers=headers)
    assert voices_response.status_code == 200
    voices = voices_response.json()
    assert len(voices) >= 1

    project_response = client.post(
        "/projects",
        data={"title": "Sample Book", "text": "Hello world", "voice_id": voices[0]["id"]},
        headers=headers,
    )
    assert project_response.status_code == 201, project_response.text
    project = project_response.json()
    assert project["title"] == "Sample Book"

    project_id = project["id"]
    # Wait for background task to finish generating placeholder audio
    for _ in range(10):
        time.sleep(0.2)
        detail_response = client.get(f"/projects/{project_id}", headers=headers)
        assert detail_response.status_code == 200
        detail = detail_response.json()
        if detail["status"] == "completed":
            break
    else:
        pytest.fail("Project did not complete in time")

    history_response = client.get("/projects", headers=headers)
    assert history_response.status_code == 200
    history = history_response.json()
    assert any(item["id"] == project_id for item in history)

    audio_response = client.get(f"/projects/{project_id}/audio", headers=headers)
    assert audio_response.status_code == 200
    assert audio_response.headers["content-type"] == "audio/wav"
    assert len(audio_response.content) > 0
