import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

DOCUMENT_BUCKET = os.getenv("SUPABASE_DOCUMENT_BUCKET", "documents")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not configured")

if not SUPABASE_SECRET_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY is not configured")


storage_client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


def upload_document(path: str, file_bytes: bytes, content_type: str):
    return (
        storage_client.storage
        .from_(DOCUMENT_BUCKET)
        .upload(
            path,
            file_bytes,
            {
                "content-type": content_type,
                "upsert": "false",
            },
        )
    )


def delete_document(path: str):
    return (
        storage_client.storage
        .from_(DOCUMENT_BUCKET)
        .remove([path])
    )