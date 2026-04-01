from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())

VALID_PDF_HEADER = b"%PDF-1.4 fake pdf content for testing purposes"


def pdf_file(name: str, content: bytes = VALID_PDF_HEADER):
    return (name, BytesIO(content), "application/pdf")


@patch("app.routers.upload.ingest_pdf", return_value=5)
def test_batch_upload_multiple_valid_pdfs(mock_ingest):
    response = client.post(
        "/upload",
        files=[
            ("files", pdf_file("a.pdf")),
            ("files", pdf_file("b.pdf")),
            ("files", pdf_file("c.pdf")),
        ],
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for item in data:
        assert "chunks" in item
        assert item["chunks"] == 5
        assert "error" not in item or item["error"] is None


@patch("app.routers.upload.ingest_pdf", return_value=5)
def test_single_file_returns_list(mock_ingest):
    response = client.post(
        "/upload",
        files=[("files", pdf_file("single.pdf"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["filename"] == "single.pdf"
    assert data[0]["chunks"] == 5


@patch("app.routers.upload.ingest_pdf", return_value=5)
def test_one_invalid_file_in_batch_best_effort(mock_ingest):
    response = client.post(
        "/upload",
        files=[
            ("files", pdf_file("good.pdf")),
            ("files", ("bad.png", BytesIO(b"not a pdf"), "image/png")),
            ("files", pdf_file("also_good.pdf")),
        ],
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["chunks"] == 5
    assert data[1]["error"] is not None
    assert data[2]["chunks"] == 5


def test_no_files_returns_400():
    response = client.post("/upload", files=[])
    assert response.status_code == 400


def test_too_many_files_returns_400():
    files = [("files", pdf_file(f"file{i}.pdf")) for i in range(51)]
    with patch("app.routers.upload.ingest_pdf", return_value=1):
        response = client.post("/upload", files=files)
    assert response.status_code == 400


@patch("app.routers.upload.ingest_pdf", return_value=7)
def test_duplicate_filename_overwritten(mock_ingest, tmp_path):
    with patch("app.config.settings") as mock_settings:
        mock_settings.uploads_dir = str(tmp_path)
        response1 = client.post(
            "/upload",
            files=[("files", pdf_file("report.pdf", b"%PDF-1.4 original"))],
        )
        response2 = client.post(
            "/upload",
            files=[("files", pdf_file("report.pdf", b"%PDF-1.4 updated"))],
        )
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response2.json()[0]["filename"] == "report.pdf"
    assert response2.json()[0]["chunks"] == 7
