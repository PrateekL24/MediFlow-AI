from typing import TypedDict, Optional


class GraphState(TypedDict):

    user_input: str
    session_id: str

    intent: Optional[str]

    patient_data: Optional[dict]
    request_data: Optional[dict]

    tool_result: Optional[dict]

    workflow_id: Optional[str]
    current_agent: Optional[str]

    # Field that the current agent is waiting for
    awaiting_input: Optional[str]

    messages: list

    response: Optional[str]

    patient_lookup: Optional[dict]
    selected_patient: Optional[dict]

    selected_doctor: Optional[dict]
    doctors_found: Optional[list]
    appointment_data: Optional[dict]

    next_step: Optional[str]
