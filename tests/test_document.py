from backend.services.document_service import DocumentService


def test_document_rejects_unsupported_type():
    result = DocumentService.upload_document(
        patient_id="patient-1",
        document_name="report.txt",
        content_type="text/plain",
        file_bytes=b"report",
    )

    assert result["success"] is False
    assert "Unsupported document type" in result["message"]


def test_document_rejects_empty_file():
    result = DocumentService.upload_document(
        patient_id="patient-1",
        document_name="report.pdf",
        content_type="application/pdf",
        file_bytes=b"",
    )

    assert result["success"] is False
    assert "empty" in result["message"]


def test_document_upload_stores_file_then_metadata(monkeypatch):
    calls = []

    monkeypatch.setattr(
        "backend.services.document_service.upload_document",
        lambda **kwargs: calls.append(("upload", kwargs)),
    )
    monkeypatch.setattr(
        "backend.services.document_service.delete_document",
        lambda path: calls.append(("delete", path)),
    )
    monkeypatch.setattr(
        "backend.services.document_service.DocumentRepository.create_document",
        lambda metadata: calls.append(("metadata", metadata)) or type(
            "Response", (), {"data": [metadata]}
        )(),
    )
    monkeypatch.setattr(
        "backend.services.document_service.AuditService.record_event",
        lambda **kwargs: calls.append(("audit", kwargs)),
    )

    result = DocumentService.upload_document(
        patient_id="patient-1",
        document_name="/tmp/blood_report.pdf",
        content_type="application/pdf",
        file_bytes=b"pdf-bytes",
        workflow_id="workflow-1",
    )

    assert result["success"] is True
    assert result["data"]["patient_id"] == "patient-1"
    assert result["data"]["document_type"] == "pdf"
    assert result["data"]["document_name"] == "blood_report.pdf"
    assert calls[0][0] == "upload"
    assert calls[1][0] == "metadata"
    assert calls[2][0] == "audit"
    assert calls[2][1]["workflow_id"] == "workflow-1"
    assert calls[2][1]["metadata"] == {"document_type": "pdf"}


def test_document_metadata_failure_removes_uploaded_file(monkeypatch):
    calls = []

    monkeypatch.setattr(
        "backend.services.document_service.upload_document",
        lambda **kwargs: calls.append(("upload", kwargs)),
    )
    monkeypatch.setattr(
        "backend.services.document_service.delete_document",
        lambda path: calls.append(("delete", path)),
    )
    monkeypatch.setattr(
        "backend.services.document_service.DocumentRepository.create_document",
        lambda metadata: (_ for _ in ()).throw(Exception("DB_ERROR")),
    )

    result = DocumentService.upload_document(
        patient_id="patient-1",
        document_name="report.pdf",
        content_type="application/pdf",
        file_bytes=b"pdf-bytes",
    )

    assert result["success"] is False
    assert calls[0][0] == "upload"
    assert calls[1][0] == "delete"
