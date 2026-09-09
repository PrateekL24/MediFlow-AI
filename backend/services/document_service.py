import os
import uuid
from pathlib import Path

from backend.core.storage import upload_document, delete_document
from backend.repositories.document_repository import DocumentRepository
from backend.services.audit_service import AuditService


ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
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

        extension = ALLOWED_DOCUMENT_TYPES.get(content_type)
        if extension is None:
            return {
                "success": False,
                "message": "Unsupported document type. Please upload a PDF, JPG, or PNG file.",
            }

        max_size = int(os.getenv("MAX_DOCUMENT_SIZE_BYTES", DEFAULT_MAX_DOCUMENT_SIZE))

        if not file_bytes:
            return {"success": False, "message": "The uploaded document is empty."}

        if len(file_bytes) > max_size:
            return {
                "success": False,
                "message": "The document is too large. Please upload a file up to 10 MB.",
            }

        document_id = str(uuid.uuid4())
        storage_path = f"{patient_id}/{document_id}.{extension}"

        try:
            upload_document(
                path=storage_path,
                file_bytes=file_bytes,
                content_type=content_type,
            )

            metadata = {
                "document_id": document_id,
                "patient_id": patient_id,
                "document_name": Path(document_name).name,
                "document_type": extension,
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
                metadata={"document_type": extension},
            )

            return {
                "success": True,
                "message": "Document uploaded successfully.",
                "data": metadata,
            }

        except Exception as exc:
            try:
                delete_document(storage_path)
            except Exception:
                pass

            return {
                "success": False,
                "message": "The document could not be uploaded. Please try again.",
                "error_type": type(exc).__name__,
            }
