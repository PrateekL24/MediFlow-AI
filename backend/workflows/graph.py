from langgraph.graph import StateGraph, END

from backend.workflows.state import GraphState

from agents.supervisor.agent import supervisor_agent
from agents.reception.agent import ReceptionAgent
from agents.registration.agent import RegistrationAgent
from agents.doctor.agent import DoctorAgent
from agents.appointment.agent import AppointmentAgent
from agents.document.agent import DocumentAgent


workflow = StateGraph(GraphState)


def run_node(node_name, handler):
    """Record the actual graph node before running its handler."""

    def wrapped(state: GraphState):
        state["current_node"] = node_name
        return handler(state)

    return wrapped


workflow.add_node(
    "supervisor",
    run_node("supervisor", supervisor_agent)
)
workflow.add_node(
    "reception",
    run_node("reception", ReceptionAgent.run)
)
workflow.add_node(
    "registration",
    run_node("registration", RegistrationAgent.run)
)
workflow.add_node(
    "doctor",
    run_node("doctor", DoctorAgent.run)
)
workflow.add_node(
    "appointment",
    run_node("appointment", AppointmentAgent.run)
)


def document_node(state: GraphState, config=None):
    state["current_node"] = "document"
    configurable = (config or {}).get("configurable", {})
    uploaded_file = configurable.get("uploaded_file")
    return DocumentAgent.run(state, uploaded_file=uploaded_file)


workflow.add_node("document", document_node)


def entry_router_node(state: GraphState):
    state["current_node"] = "entry_router"
    return state


def entry_route(state: GraphState):
    current_agent = state.get("current_agent")
    awaiting_input = state.get("awaiting_input")
    intent = state.get("intent")
    user_input = (state.get("user_input") or "").strip()

    if current_agent == "Reception" and awaiting_input in ["phone", "patient_selection"]:
        return "reception"

    if current_agent == "Registration" and awaiting_input:
        return "registration"

    if current_agent == "Doctor" and awaiting_input == "doctor_selection":
        return "doctor"

    if current_agent == "Appointment" and awaiting_input:
        return "appointment"

    if current_agent == "Document" and awaiting_input == "document_upload":
        return "document"

    doctor_intents = [
        "doctor_recommendation",
        "doctor_fee",
        "doctor_availability",
    ]

    if intent in doctor_intents and not user_input:
        return "doctor"

    patient_action_intents = [
        "register_patient",
        "book_appointment",
        "upload_document",
        "follow_up",
    ]

    if intent == "book_appointment" and not user_input:
        return "appointment"

    if intent in patient_action_intents and not user_input:
        return "reception"

    return "supervisor"


def supervisor_route(state: GraphState):
    intent = state.get("intent")
    user_input = (state.get("user_input") or "").lower()

    patient_action_intents = [
        "register_patient",
        "book_appointment",
        "upload_document",
        "follow_up",
    ]

    doctor_intents = [
        "doctor_recommendation",
        "doctor_fee",
        "doctor_availability",
    ]

    if (
        intent == "doctor_availability"
        and (
            "appointment" in user_input
            or "booking" in user_input
            or "slot" in user_input
        )
    ):
        return "appointment"

    if intent in patient_action_intents:
        if intent == "book_appointment":
            return "appointment"
        if intent == "upload_document":
            return "reception"
        return "reception"

    if intent in doctor_intents:
        return "doctor"

    return END


def reception_route(state: GraphState):
    next_step = state.get("next_step")
    intent = state.get("intent")
    appointment_data = state.get("appointment_data") or {}
    selected_patient = state.get("selected_patient")

    if next_step == "registration":
        return "registration"

    if next_step == "document" and selected_patient:
        return "document"

    # A selected slot means the appointment workflow is waiting for the
    # patient-identification step to finish, even for an availability-first
    # request whose intent is doctor_availability.
    if (
        selected_patient
        and appointment_data.get("slot_id")
        and appointment_data.get("doctor_id")
        and appointment_data.get("appointment_date")
        and appointment_data.get("appointment_time")
    ):
        return "appointment"

    if next_step == "appointment" and selected_patient:
        return "appointment"

    if intent == "book_appointment" and selected_patient:
        return "appointment"

    return END


def registration_route(state: GraphState):
    appointment_data = state.get("appointment_data") or {}
    selected_patient = state.get("selected_patient")

    if selected_patient and (
        state.get("intent") == "book_appointment"
        or appointment_data.get("booking_confirmed")
        or appointment_data.get("slot_id")
    ):
        return "appointment"

    return END


def appointment_route(state: GraphState):
    if state.get("next_step") == "reception":
        return "reception"

    return END


workflow.add_node("entry_router", entry_router_node)
workflow.set_entry_point("entry_router")

workflow.add_conditional_edges("entry_router", entry_route)
workflow.add_conditional_edges("supervisor", supervisor_route)
workflow.add_conditional_edges("reception", reception_route)
workflow.add_conditional_edges("registration", registration_route)
workflow.add_edge("doctor", END)
workflow.add_conditional_edges("appointment", appointment_route)
workflow.add_edge("document", END)

graph = workflow.compile()
