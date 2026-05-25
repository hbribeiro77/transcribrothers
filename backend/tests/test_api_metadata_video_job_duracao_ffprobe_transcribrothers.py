from starlette.testclient import TestClient

from transcribrothers_backend.main import app


def test_metadata_video_job_inexistente_retorna_404() -> None:
    with TestClient(app) as client:
        r = client.get("/api/jobs/job-inexistente-metadata-video/video/metadata")
        assert r.status_code == 404
