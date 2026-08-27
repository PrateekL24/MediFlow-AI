from fastapi import APIRouter
from pydantic import BaseModel

from backend.workflows.graph import graph

router = APIRouter()


class ConversationRequest(BaseModel):
    message: str


@router.post("/conversation")
def conversation(request: ConversationRequest):

    state = {

        "user_input": request.message,

        "session_id": "demo-session",

        "intent": None,

        "patient_data": None,

        "tool_result": None,

        "workflow_id": None,

        "current_agent": None,

        "messages": [],

        "response": None

    }

    result = graph.invoke(state)

    return result