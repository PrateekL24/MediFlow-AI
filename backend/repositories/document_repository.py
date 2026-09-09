from backend.core.database import supabase


class DocumentRepository:

    @staticmethod
    def create_document(document_data: dict):
        return (
            supabase
            .table("documents")
            .insert(document_data)
            .execute()
        )
