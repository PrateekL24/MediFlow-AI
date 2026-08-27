from backend.tools.doctor_tool import DoctorTool
from backend.utils.input_parser import clean_text


def parse_doctor_selection(value: str, doctors: list):

    text = clean_text(value)

    if text.isdigit():

        index = int(text) - 1

        if 0 <= index < len(doctors):
            return doctors[index]

        return None

    matches = []

    for doctor in doctors:

        doctor_name = clean_text(
            doctor.get("doctor_name", "")
        )

        if doctor_name and doctor_name in text:
            matches.append(doctor)

    if len(matches) == 1:
        return matches[0]

    return None


class DoctorAgent:

    @staticmethod
    def run(state):

        intent = state.get("intent")
        request_data = state.get("request_data") or {}

        if state.get("awaiting_input") == "doctor_selection":

            doctors = state.get("doctors_found") or []

            selected_doctor = parse_doctor_selection(
                state.get("user_input", ""),
                doctors
            )

            if selected_doctor is None:

                state["current_agent"] = "Doctor"
                state["awaiting_input"] = "doctor_selection"
                state["response"] = (
                    "I couldn't identify the doctor. "
                    "Please enter the number or name "
                    "of the doctor."
                )

                return state

            state["selected_doctor"] = selected_doctor
            state["awaiting_input"] = None
            state["current_agent"] = None

            request_data["doctor_name"] = selected_doctor.get(
                "doctor_name",
                ""
            )
            state["request_data"] = request_data

        doctor_name = request_data.get(
            "doctor_name",
            ""
        ).strip()

        symptom = request_data.get(
            "symptom",
            ""
        ).strip()

        # ---------------------------------------
        # Doctor recommendation
        # ---------------------------------------

        if intent == "doctor_recommendation":

            if not symptom:

                state["response"] = (
                    "Please tell me what symptom or "
                    "health problem you are experiencing."
                )

                return state

            # Simple mapping for our current demo.
            # Later this can be replaced with a proper
            # medical knowledge/RAG layer.
            symptom_mapping = {
                "back pain": "Orthopedics",
                "joint pain": "Orthopedics",
                "bone pain": "Orthopedics",
                "skin": "Dermatology",
                "skin problem": "Dermatology",
                "heart": "Cardiology",
                "chest pain": "Cardiology",
                "ear": "ENT",
                "throat": "ENT",
                "headache": "Neurology",
                "migraine": "Neurology"
            }

            specialization = None

            symptom_lower = symptom.lower()

            for keyword, specialist in symptom_mapping.items():

                if keyword in symptom_lower:

                    specialization = specialist
                    break

            if not specialization:

                state["response"] = (
                    "I couldn't determine the appropriate "
                    "specialist from that symptom. "
                    "Please provide a little more detail."
                )

                return state

            result = (
                DoctorTool
                .find_doctors_by_specialization(
                    specialization
                )
            )

            doctors = result.get(
                "doctors",
                []
            )

            if not doctors:

                state["response"] = (
                    f"I couldn't find an available "
                    f"{specialization} doctor."
                )

                return state

            doctor_list = []

            for index, doctor in enumerate(
                doctors,
                start=1
            ):

                doctor_list.append(
                    f"{index}. "
                    f"{doctor.get('doctor_name', '')} "
                    f"({doctor.get('experience_years', '')} "
                    f"years experience)"
                )

            state["response"] = (
                f"For {symptom}, I recommend consulting "
                f"a {specialization} specialist.\n\n"
                + "\n".join(doctor_list)
            )

            state["doctors_found"] = doctors

            return state

        # ---------------------------------------
        # Doctor fee
        # ---------------------------------------

        if intent == "doctor_fee":

            if not doctor_name:

                state["response"] = (
                    "Which doctor's consultation fee "
                    "would you like to know?"
                )

                return state

            result = DoctorTool.find_doctors_by_name(
                doctor_name
            )

            doctors = result.get(
                "doctors",
                []
            )

            if not doctors:

                state["response"] = (
                    f"I couldn't find a doctor matching "
                    f"'{doctor_name}'."
                )

                return state

            if len(doctors) > 1:

                doctor_list = []

                for index, doctor in enumerate(
                    doctors,
                    start=1
                ):

                    doctor_list.append(
                        f"{index}. "
                        f"{doctor.get('doctor_name', '')} "
                        f"- ₹{doctor.get('consultation_fee', '')}"
                    )

                state["response"] = (
                    "I found multiple doctors:\n\n"
                    + "\n".join(doctor_list)
                    + "\n\nWhich doctor do you mean?"
                )

                state["doctors_found"] = doctors
                state["current_agent"] = "Doctor"
                state["awaiting_input"] = "doctor_selection"

                return state

            doctor = doctors[0]

            state["response"] = (
                f"The consultation fee for "
                f"{doctor.get('doctor_name', '')} "
                f"is ₹{doctor.get('consultation_fee', '')}."
            )

            state["selected_doctor"] = doctor
            state["current_agent"] = None
            state["awaiting_input"] = None

            return state

        # ---------------------------------------
        # Doctor availability
        # ---------------------------------------

        if intent == "doctor_availability":

            if not doctor_name:

                state["response"] = (
                    "Which doctor's availability "
                    "would you like to check?"
                )

                return state

            result = DoctorTool.find_doctors_by_name(
                doctor_name
            )

            doctors = result.get(
                "doctors",
                []
            )

            if not doctors:

                state["response"] = (
                    f"I couldn't find a doctor matching "
                    f"'{doctor_name}'."
                )

                return state

            if len(doctors) > 1:

                doctor_list = []

                for index, doctor in enumerate(
                    doctors,
                    start=1
                ):

                    doctor_list.append(
                        f"{index}. "
                        f"{doctor.get('doctor_name', '')}"
                    )

                state["response"] = (
                    "I found multiple doctors:\n\n"
                    + "\n".join(doctor_list)
                    + "\n\nWhich doctor do you mean?"
                )

                state["doctors_found"] = doctors
                state["current_agent"] = "Doctor"
                state["awaiting_input"] = "doctor_selection"

                return state

            doctor = doctors[0]

            state["response"] = (
                f"{doctor.get('doctor_name', '')} "
                f"is available on "
                f"{doctor.get('available_days', '')} "
                f"from "
                f"{doctor.get('available_time', '')}."
            )

            state["selected_doctor"] = doctor
            state["current_agent"] = None
            state["awaiting_input"] = None

            return state

        # ---------------------------------------
        # Unsupported intent
        # ---------------------------------------

        state["response"] = (
            "I can help you with doctor "
            "recommendations, consultation fees, "
            "and doctor availability."
        )

        return state
