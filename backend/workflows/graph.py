from langgraph.graph import StateGraph, END

from backend.workflows.state import GraphState

from agents.supervisor.agent import supervisor_agent
from agents.reception.agent import ReceptionAgent
from agents.registration.agent import RegistrationAgent
from agents.doctor.agent import DoctorAgent
from agents.appointment.agent import AppointmentAgent


# ---------------------------------------
# Build Graph
# ---------------------------------------

workflow = StateGraph(GraphState)


# ---------------------------------------
# Nodes
# ---------------------------------------

workflow.add_node(
    "supervisor",
    supervisor_agent
)

workflow.add_node(
    "reception",
    ReceptionAgent.run
)

workflow.add_node(
    "registration",
    RegistrationAgent.run
)

workflow.add_node(
    "doctor",
    DoctorAgent.run
)

workflow.add_node(
    "appointment",
    AppointmentAgent.run
)


# ---------------------------------------
# Entry Routing
#
# Python decides whether this is:
# - Reception follow-up
# - Registration follow-up
# - Doctor follow-up
# - Appointment follow-up
# - New request
#
# This prevents unnecessary Gemini calls.
# ---------------------------------------

def entry_route(state: GraphState):

    current_agent = state.get("current_agent")
    awaiting_input = state.get("awaiting_input")
    intent = state.get("intent")

    user_input = (
        state.get("user_input") or ""
    ).strip()

    # -----------------------------------
    # Reception is waiting for input
    # -----------------------------------

    if (
        current_agent == "Reception"
        and awaiting_input in [
            "phone",
            "patient_selection"
        ]
    ):
        return "reception"

    # -----------------------------------
    # Registration is waiting for input
    # -----------------------------------

    if (
        current_agent == "Registration"
        and awaiting_input
    ):
        return "registration"

    # -----------------------------------
    # Doctor is waiting for input
    # -----------------------------------

    if (
        current_agent == "Doctor"
        and awaiting_input == "doctor_selection"
    ):
        return "doctor"

    # -----------------------------------
    # Appointment is waiting for input
    # -----------------------------------

    if (
        current_agent == "Appointment"
        and awaiting_input
    ):
        return "appointment"

    # -----------------------------------
    # Doctor intents without new input
    # -----------------------------------

    doctor_intents = [
        "doctor_recommendation",
        "doctor_fee",
        "doctor_availability"
    ]

    if intent in doctor_intents and not user_input:
        return "doctor"

    # -----------------------------------
    # Existing patient intent without new
    # user input
    # -----------------------------------

    patient_action_intents = [
        "register_patient",
        "book_appointment",
        "upload_document",
        "follow_up"
    ]

    if (
        intent == "book_appointment"
        and not user_input
    ):
        return "appointment"

    if (
        intent in patient_action_intents
        and not user_input
    ):
        return "reception"

    # -----------------------------------
    # New request
    #
    # Gemini is required here to understand
    # the user's natural-language request.
    # -----------------------------------

    return "supervisor"


# ---------------------------------------
# Supervisor Routing
# ---------------------------------------

def supervisor_route(state: GraphState):

    intent = state.get("intent")

    user_input = (
        state.get("user_input") or ""
    ).lower()

    patient_action_intents = [
        "register_patient",
        "book_appointment",
        "upload_document",
        "follow_up"
    ]

    doctor_intents = [
        "doctor_recommendation",
        "doctor_fee",
        "doctor_availability"
    ]

    # -----------------------------------
    # Doctor availability request that is
    # specifically asking for appointment/
    # booking slots
    # -----------------------------------

    if (
        intent == "doctor_availability"
        and (
            "appointment" in user_input
            or "booking" in user_input
            or "slot" in user_input
        )
    ):
        return "appointment"

    # -----------------------------------
    # Patient-related requests
    # -----------------------------------

    if intent in patient_action_intents:

        if intent == "book_appointment":
            return "appointment"

        return "reception"

    # -----------------------------------
    # Doctor-related requests
    # -----------------------------------

    if intent in doctor_intents:
        return "doctor"

    # -----------------------------------
    # Greeting / general inquiry / unknown
    # -----------------------------------

    return END


# ---------------------------------------
# Reception Routing
# ---------------------------------------

def reception_route(state: GraphState):

    next_step = state.get("next_step")
    intent = state.get("intent")

    # -----------------------------------
    # New patient registration
    # -----------------------------------

    if next_step == "registration":
        return "registration"

    # -----------------------------------
    # Availability-first booking flow
    #
    # If booking has already been confirmed
    # and patient has been identified, continue
    # to AppointmentAgent.
    # -----------------------------------

    if (
        next_step == "appointment"
        and state.get("selected_patient")
    ):
        return "appointment"

    # -----------------------------------
    # Backward compatibility for the original
    # direct book_appointment flow
    # -----------------------------------

    if (
        intent == "book_appointment"
        and state.get("selected_patient")
    ):
        return "appointment"

    return END


# ---------------------------------------
# Registration Routing
# ---------------------------------------

def registration_route(state: GraphState):

    appointment_data = (
        state.get("appointment_data") or {}
    )

    # -----------------------------------
    # Continue booking after successful
    # new-patient registration.
    #
    # This supports both:
    #
    # intent == "book_appointment"
    #
    # and the availability-first flow:
    #
    # intent == "doctor_availability"
    # booking_confirmed == True
    # -----------------------------------

    if (
        state.get("selected_patient")
        and (
            state.get("intent") == "book_appointment"
            or appointment_data.get("booking_confirmed")
        )
    ):
        return "appointment"

    return END


# ---------------------------------------
# Appointment Routing
# ---------------------------------------

def appointment_route(state: GraphState):

    # -----------------------------------
    # AppointmentAgent may request
    # patient identification.
    # -----------------------------------

    if state.get("next_step") == "reception":
        return "reception"

    return END


# ---------------------------------------
# Entry Point
# ---------------------------------------

workflow.set_entry_point(
    "entry_router"
)

workflow.add_node(
    "entry_router",
    lambda state: state
)

workflow.add_conditional_edges(
    "entry_router",
    entry_route
)


# ---------------------------------------
# Supervisor Routing
# ---------------------------------------

workflow.add_conditional_edges(
    "supervisor",
    supervisor_route
)


# ---------------------------------------
# Reception Routing
# ---------------------------------------

workflow.add_conditional_edges(
    "reception",
    reception_route
)


# ---------------------------------------
# Registration Routing
# ---------------------------------------

workflow.add_conditional_edges(
    "registration",
    registration_route
)


# ---------------------------------------
# Doctor → END
# ---------------------------------------

workflow.add_edge(
    "doctor",
    END
)


# ---------------------------------------
# Appointment Routing
# ---------------------------------------

workflow.add_conditional_edges(
    "appointment",
    appointment_route
)


# ---------------------------------------
# Compile
# ---------------------------------------

graph = workflow.compile()