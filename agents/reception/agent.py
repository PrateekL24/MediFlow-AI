from backend.workflows import state
from backend.workflows.state import GraphState
from backend.tools.patient_tool import PatientTool
import time

from backend.utils.input_parser import (
    parse_phone,
    parse_selection
)


class ReceptionAgent:

    @staticmethod
    def run(state: GraphState):

        patient_data = state.get("patient_data") or {}

        print(
            f"\n[{time.strftime('%H:%M:%S')}] "
            "Reception started"
        )

        if state.get("awaiting_input") == "phone":
            patient_data["phone"] = state.get(
                "user_input",
                ""
            ).strip()
            state["patient_data"] = patient_data

        if state.get("awaiting_input") == "patient_selection":
            user_input = state.get("user_input", "")
            patients = (
                state.get("patient_lookup", {})
                .get("patients", [])
            )

            selected_patient = parse_selection(user_input, patients)

            if selected_patient is None:
                state["current_agent"] = "Reception"
                state["awaiting_input"] = "patient_selection"
                state["response"] = (
                    "I couldn't identify the patient. "
                    "Please enter the number or name of the patient."
                )
                return state

            state["selected_patient"] = selected_patient
            state["awaiting_input"] = None

            appointment_data = state.get("appointment_data") or {}

            if state.get("intent") == "upload_document":
                state["next_step"] = "document"
            elif (
                state.get("intent") == "book_appointment"
                or appointment_data.get("booking_confirmed")
            ):
                state["next_step"] = "appointment"
            else:
                state["next_step"] = "continue"

            first_name = selected_patient.get("first_name", "there")
            state["response"] = f"Thanks. I've selected {first_name}."
            state["current_agent"] = None
            return state

        phone = patient_data.get("phone", "").strip()

        if not phone:
            state["current_agent"] = "Reception"
            state["awaiting_input"] = "phone"
            state["response"] = (
                "Sure. Before I continue, may I have your mobile number?"
            )
            return state

        valid_phone = parse_phone(phone)

        if valid_phone is None:
            state["current_agent"] = "Reception"
            state["awaiting_input"] = "phone"
            state["response"] = (
                "That doesn't look like a valid mobile number. "
                "Please enter your 10-digit mobile number."
            )
            return state

        state["patient_data"]["phone"] = valid_phone

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            "Supabase patient lookup started"
        )

        start_time = time.perf_counter()
        result = PatientTool.find_patients_by_phone(valid_phone)
        elapsed = time.perf_counter() - start_time

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"Supabase patient lookup completed | "
            f"{elapsed:.2f} sec"
        )

        count = result.get("count", 0)
        state["patient_lookup"] = result
        state["awaiting_input"] = None

        if count == 0:
            state["next_step"] = "registration"
            state["response"] = (
                "I couldn't find an existing patient record with this mobile number. "
                "Let's register you first."
            )
            state["current_agent"] = "Reception"
            return state

        if count == 1:
            patient = result["patients"][0]
            state["selected_patient"] = patient

            appointment_data = state.get("appointment_data") or {}

            if state.get("intent") == "upload_document":
                state["next_step"] = "document"
            elif (
                state.get("intent") == "book_appointment"
                or appointment_data.get("booking_confirmed")
            ):
                state["next_step"] = "appointment"
            else:
                state["next_step"] = "continue"

            first_name = patient.get("first_name", "there")
            state["response"] = f"Welcome back, {first_name}."
            state["current_agent"] = None
            return state

        patient_list = []

        for index, patient in enumerate(result["patients"], start=1):
            first_name = patient.get("first_name", "")
            last_name = patient.get("last_name", "")
            age = patient.get("age", "")
            full_name = f"{first_name} {last_name}".strip()
            patient_list.append(f"{index}. {full_name} (Age: {age})")

        state["next_step"] = "select_patient"
        state["awaiting_input"] = "patient_selection"
        state["current_agent"] = "Reception"
        state["response"] = (
            "I found multiple patient records linked to this mobile number:\n\n"
            + "\n".join(patient_list)
            + "\n\nWhich patient is visiting today?"
        )

        return state
