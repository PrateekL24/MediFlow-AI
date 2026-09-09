import os
import uuid
from pathlib import Path

from backend.core.storage import upload_document, delete_document
from backend.repositories.document_repository import DocumentRepository
from backend.services.audit_service import AuditService


ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": {"extension": "pdf", "extensions": {".pdf"}, "signature": b"%PDF-"},
    "image/jpeg": {"extension": "jpg", "extensions": {".jpg", ".jpeg"}, "signature": b"\xff\xd8\xff"},
    "image/png": {"extension": "png", "extensions": {".png"}, "signature": b"\x89PNG\r\n\x1a\n"},
}

DEFAULT_MAX_DOCUMENT_SIZE = 10 * 1024 * 1024


class DocumentService:

    @staticmethod
    def upload_document(
        patient_id: str,
        document_name: str,
        content_type: str,
        file_bytes: bytes,
        workflow_id: str | None = None,
    ):
        if not patient_id:
            return {"success": False, "message": "Patient identification is required."}

        if not document_name or not document_name.strip():
            return {"success": False, "message": "Document name is required."}

        document_type = ALLOWED_DOCUMENT_TYPES.get(content_type)
        if document_type is None:
            return {
                "success": False,
                "message": "Unsupported document type. Please upload a PDF, JPG, or PNG file.",
            }

        filename = Path(document_name).name
        extension = Path(filename).suffix.lower()

        if extension not in document_type["extensions"]:
            return {
                "success": False,
                "message": "The document extension does not match its file type.",
            }

        max_size = int(os.getenv("MAX_DOCUMENT_SIZE_BYTES", DEFAULT_MAX_DOCUMENT_SIZE))

        if not file_bytes:
            return {"success": False, "message": "The uploaded document is empty."}

        if len(file_bytes) > max_size:
            return {
                "success": False,
                "message": "The document is too large. Please upload a file up to 10 MB.",
            }

        if not file_bytes.startswith(document_type["signature"]):
            return {
                "success": False,
                "message": "The uploaded file does not appear to be a valid document of the selected type.",
            }

        document_id = str(uuid.uuid4())
        storage_path = f"{patient_id}/{document_id}.{document_type['extension']}"

        try:
            upload_document(
                path=storage_path,
                file_bytes=file_bytes,
                content_type=content_type,
            )

            metadata = {
                "document_id": document_id,
                "patient_id": patient_id,
                "document_name": filename,
                "document_type": document_type["extension"],
                "file_path": storage_path,
            }

            result = DocumentRepository.create_document(metadata)

            if not getattr(result, "data", None):
                raise RuntimeError("Document metadata could not be stored.")

            AuditService.record_event(
                workflow_id=workflow_id,
                agent_name="Document",
                tool_name="DocumentTool",
                action="document_uploaded",
                status="success",
                metadata={"document_type": document_type["extension"]},
            )

            return {
                "success": True,
                "message": "Document uploaded successfully.",
                "data": metadata,
            }

        except Exception as exc:
            try:
                delete_document(storage_path)
            except Exception as cleanup_exc:
                print(
                    "Document storage cleanup failed: "
                    f"{cleanup_exc}"
                )

            return {
                "success": False,
                "message": "The document could not be uploaded. Please try again.",
                "error_type": type(exc).__name__,
            }
