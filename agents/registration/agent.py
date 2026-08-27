from backend.workflows.state import GraphState
from backend.tools.patient_tool import PatientTool
import time

from backend.utils.input_parser import (
    parse_registration_input,
    parse_phone,
    parse_age
)


class RegistrationAgent:

    @staticmethod
    def run(state: GraphState):

        patient_data = state.get("patient_data") or {}

        user_input = state.get(
            "user_input",
            ""
        ).strip()

        awaiting_input = state.get(
            "awaiting_input"
        )

        print(
            f"\n[{time.strftime('%H:%M:%S')}] "
            "Registration started"
        )

        # ---------------------------------------
        # Capture current user input
        # ---------------------------------------

        if awaiting_input == "first_name":

            extracted = parse_registration_input(
                user_input
            )

            if extracted.get("first_name"):
                patient_data["first_name"] = (
                    extracted["first_name"]
                )
            else:
                patient_data["first_name"] = user_input

            # Also capture age if user gives:
            # Raj, 30
            if extracted.get("age") is not None:
                patient_data["age"] = extracted["age"]

        elif awaiting_input == "age":

            age = parse_age(user_input)

            if age is None:

                state["current_agent"] = "Registration"
                state["awaiting_input"] = "age"

                state["response"] = (
                    "Please enter a valid age between "
                    "1 and 120."
                )

                return state

            patient_data["age"] = age

        elif awaiting_input == "phone":

            phone = parse_phone(user_input)

            if phone is None:

                state["current_agent"] = "Registration"
                state["awaiting_input"] = "phone"

                state["response"] = (
                    "Please enter a valid 10-digit "
                    "mobile number."
                )

                return state

            patient_data["phone"] = phone

        # ---------------------------------------
        # Save updated patient data
        # ---------------------------------------

        state["patient_data"] = patient_data

        # ---------------------------------------
        # Check required fields
        # ---------------------------------------

        required_fields = [
            "first_name",
            "age",
            "phone"
        ]

        missing_fields = []

        for field in required_fields:

            value = patient_data.get(field)

            if value is None or value == "":
                missing_fields.append(field)

        # ---------------------------------------
        # Still missing information
        # ---------------------------------------

        if missing_fields:

            field = missing_fields[0]

            state["current_agent"] = "Registration"
            state["awaiting_input"] = field

            questions = {
                "first_name": (
                    "May I have your first name?"
                ),
                "age": (
                    "May I know your age?"
                ),
                "phone": (
                    "May I have your mobile number?"
                )
            }

            state["response"] = questions[field]

            return state

        # ---------------------------------------
        # All registration information available
        # ---------------------------------------

        print("\n===== REGISTRATION DATA =====")
        print(patient_data)

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            "Supabase patient creation started"
        )

        start_time = time.perf_counter()

        result = PatientTool.create_patient(
            patient_data
        )

        elapsed = time.perf_counter() - start_time

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"Supabase patient creation completed | "
            f"{elapsed:.2f} sec"
        )

        state["tool_result"] = result

        # ---------------------------------------
        # Registration failed
        # ---------------------------------------

        if not result.get("success"):

            state["current_agent"] = "Registration"

            state["response"] = result.get(
                "message",
                "Registration could not be completed."
            )

            return state

        # ---------------------------------------
        # Registration successful
        # ---------------------------------------

        created_patient = None

        if result.get("data"):
            created_patient = result["data"][0]

        if created_patient:
            state["selected_patient"] = created_patient

        state["awaiting_input"] = None
        state["next_step"] = "continue"
        state["current_agent"] = None

        first_name = patient_data.get(
            "first_name",
            "there"
        )

        state["response"] = (
            f"You're registered successfully, "
            f"{first_name}."
        )

        return state