from agents.document.agent import DocumentAgent
from backend.workflows.graph import entry_route, reception_route


def test_document_request_routes_to_reception_for_patient_identification():
    state = {
        "current_agent": None,
        "awaiting_input": None,
        "intent": "upload_document",
        "user_input": "I want to upload a report",
    }

    assert entry_route(state) == "supervisor"


def test_document_waiting_input_routes_to_document():
    state = {
        "current_agent": "Document",
        "awaiting_input": "document_upload",
        "intent": "upload_document",
        "user_input": "",
    }

    assert entry_route(state) == "document"


def test_selected_patient_routes_reception_to_document():
    state = {
        "next_step": "document",
        "intent": "upload_document",
        "selected_patient": {"patient_id": "patient-1"},
        "appointment_data": {},
    }

    assert reception_route(state) == "document"


def test_document_agent_waits_for_upload_when_patient_is_known():
    state = {
        "selected_patient": {"patient_id": "patient-1"},
        "current_agent": None,
        "awaiting_input": None,
        "response": None,
    }

    result = DocumentAgent.run(state, uploaded_file=None)

    assert result["current_agent"] == "Document"
    assert result["awaiting_input"] == "document_upload"
