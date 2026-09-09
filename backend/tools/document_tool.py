from backend.services.document_service import DocumentService


class DocumentTool:

    @staticmethod
    def upload_document(
        patient_id: str,
        document_name: str,
        content_type: str,
        file_bytes: bytes,
        workflow_id: str | None = None,
    ):
        return DocumentService.upload_document(
            patient_id=patient_id,
            document_name=document_name,
            content_type=content_type,
            file_bytes=file_bytes,
            workflow_id=workflow_id,
        )
