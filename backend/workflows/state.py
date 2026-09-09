from typing import TypedDict, Optional


class GraphState(TypedDict):

    # ---------------------------------------
    # Conversation
    # ---------------------------------------

    user_input: str
    session_id: str
    messages: list

    # ---------------------------------------
    # Supervisor / Coordinator
    # ---------------------------------------

    intent: Optional[str]

    # ---------------------------------------
    # Patient information
    # ---------------------------------------

    patient_data: Optional[dict]
    patient_lookup: Optional[dict]
    selected_patient: Optional[dict]

    # ---------------------------------------
    # Request information
    # ---------------------------------------

    request_data: Optional[dict]

    # ---------------------------------------
    # Doctor information
    # ---------------------------------------

    selected_doctor: Optional[dict]
    doctors_found: Optional[list]

    # ---------------------------------------
    # Appointment information
    # ---------------------------------------

    appointment_data: Optional[dict]

    # ---------------------------------------
    # Document information
    # ---------------------------------------

    document_data: Optional[dict]

    # ---------------------------------------
    # Agent / Tool output
    # ---------------------------------------

    tool_result: Optional[dict]

    # ---------------------------------------
    # Workflow tracking
    # ---------------------------------------

    workflow_id: Optional[str]
    current_node: Optional[str]
    current_agent: Optional[str]
    awaiting_input: Optional[str]
    next_step: Optional[str]

    # ---------------------------------------
    # Workflow lifecycle
    # ---------------------------------------

    workflow_status: Optional[str]

    # ---------------------------------------
    # Error tracking
    # ---------------------------------------

    last_error: Optional[str]

    # ---------------------------------------
    # User-facing response
    # ---------------------------------------

    response: Optional[str]
