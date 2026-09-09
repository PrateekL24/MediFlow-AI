import os

from dotenv import load_dotenv
from pathlib import Path

from backend.core.database import supabase


load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

DOCUMENT_BUCKET = os.getenv("SUPABASE_DOCUMENT_BUCKET", "documents")


def upload_document(path: str, file_bytes: bytes, content_type: str):
    return (
        supabase.storage
        .from_(DOCUMENT_BUCKET)
        .upload(
            path,
            file_bytes,
            {"content-type": content_type, "upsert": "false"},
        )
    )


def delete_document(path: str):
    return (
        supabase.storage
        .from_(DOCUMENT_BUCKET)
        .remove([path])
    )
