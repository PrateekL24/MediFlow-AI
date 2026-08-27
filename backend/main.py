from fastapi import FastAPI

from backend.api.registration import router as registration_router
from backend.api.conversation import router as conversation_router

app = FastAPI(
    title="MediFlow AI",
    version="1.0.0"
)

app.include_router(registration_router)
app.include_router(conversation_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to MediFlow AI 🚑"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }