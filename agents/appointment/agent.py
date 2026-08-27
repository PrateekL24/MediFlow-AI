from datetime import date, datetime, timedelta

from backend.tools.appointment_tool import AppointmentTool
from backend.tools.doctor_tool import DoctorTool


# ---------------------------------------
# Date Parsing
# ---------------------------------------

def parse_appointment_date(value: str):

    text = value.strip().lower()

    if text == "today":
        return date.today().isoformat()

    if text == "tomorrow":
        return (
            date.today() + timedelta(days=1)
        ).isoformat()

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    if text in weekdays:

        today = date.today()

        days_ahead = (
            weekdays[text] - today.weekday()
        ) % 7

        if days_ahead == 0:
            days_ahead = 7

        return (
            today + timedelta(days=days_ahead)
        ).isoformat()

    try:

        return datetime.strptime(
            text,
            "%Y-%m-%d"
        ).date().isoformat()

    except ValueError:

        return None


def parse_date_from_text(value: str):

    words = (
        value.replace(".", " ")
        .replace(",", " ")
        .split()
    )

    for word in words:

        parsed = parse_appointment_date(word)

        if parsed is not None:
            return parsed

    return None


# ---------------------------------------
# Direct Booking Detection
# ---------------------------------------

def is_direct_booking(value: str):

    text = value.strip().lower()

    direct_phrases = [
        "i want to book",
        "book an appointment",
        "book appointment",
        "book dr",
        "book this doctor",
        "please book"
    ]

    return any(
        phrase in text
        for phrase in direct_phrases
    )


# ---------------------------------------
# Booking Confirmation
# ---------------------------------------

def parse_booking_confirmation(value: str):

    text = value.strip().lower()

    yes_values = [
        "yes",
        "y",
        "sure",
        "ok",
        "okay",
        "book",
        "book it",
        "please book"
    ]

    no_values = [
        "no",
        "n",
        "no thanks",
        "not now",
        "cancel"
    ]

    if text in yes_values:
        return True

    if text in no_values:
        return False

    return None


# ---------------------------------------
# Parse "Yes 2"
#
# Returns:
#
# {
#     "confirmed": True,
#     "slot_number": 2
# }
#
# or
#
# {
#     "confirmed": True,
#     "slot_number": None
# }
#
# or None for invalid input
# ---------------------------------------

def parse_booking_confirmation_with_slot(value: str):

    text = value.strip().lower()

    # -----------------------------------
    # Exact yes/no handling
    # -----------------------------------

    confirmed = parse_booking_confirmation(text)

    if confirmed is not None:

        return {
            "confirmed": confirmed,
            "slot_number": None
        }

    # -----------------------------------
    # Handle:
    #
    # yes 2
    # y 2
    # sure 2
    # book 2
    # book it 2
    # -----------------------------------

    parts = text.split()

    if len(parts) >= 2:

        first_part = parts[0]

        yes_words = [
            "yes",
            "y",
            "sure",
            "ok",
            "okay",
            "book"
        ]

        if first_part in yes_words:

            for part in parts[1:]:

                if part.isdigit():

                    return {
                        "confirmed": True,
                        "slot_number": int(part)
                    }

    # -----------------------------------
    # Handle:
    #
    # "yes, 2"
    # "yes - 2"
    # "yes,slot 2"
    # -----------------------------------

    cleaned = (
        text.replace(",", " ")
        .replace("-", " ")
        .replace("slot", " ")
    )

    parts = cleaned.split()

    if len(parts) >= 2:

        if parts[0] in [
            "yes",
            "y",
            "sure",
            "ok",
            "okay",
            "book"
        ]:

            for part in parts[1:]:

                if part.isdigit():

                    return {
                        "confirmed": True,
                        "slot_number": int(part)
                    }

    return None


# ---------------------------------------
# Slot Selection
# ---------------------------------------

def parse_slot_selection(value: str, slots: list):

    text = value.strip()

    if not text.isdigit():
        return None

    index = int(text) - 1

    if 0 <= index < len(slots):
        return slots[index]

    return None


# ---------------------------------------
# Doctor Selection
# ---------------------------------------

def parse_doctor_selection(value: str, doctors: list):

    text = value.strip().lower()

    if text.isdigit():

        index = int(text) - 1

        if 0 <= index < len(doctors):
            return doctors[index]

        return None

    matches = []

    for doctor in doctors:

        doctor_name = (
            doctor.get("doctor_name", "")
            .strip()
            .lower()
        )

        if doctor_name and doctor_name in text:
            matches.append(doctor)

    if len(matches) == 1:
        return matches[0]

    return None


# ---------------------------------------
# Slot Time Formatting
# ---------------------------------------

def format_slot_time(slot: dict):

    start_time = slot.get(
        "start_time",
        ""
    )

    try:

        parsed = datetime.fromisoformat(
            start_time
        )

        return parsed.strftime("%H:%M")

    except ValueError:

        return start_time


# ---------------------------------------
# Appointment Agent
# ---------------------------------------

class AppointmentAgent:

    @staticmethod
    def run(state):

        appointment_data = (
            state.get("appointment_data") or {}
        )

        request_data = (
            state.get("request_data") or {}
        )

        user_input = (
            state.get("user_input") or ""
        ).strip()

        awaiting_input = state.get(
            "awaiting_input"
        )

        selected_patient = state.get(
            "selected_patient"
        )

        selected_doctor = state.get(
            "selected_doctor"
        )

        # -----------------------------------
        # Restore patient context
        # -----------------------------------

        if selected_patient:

            appointment_data["patient_id"] = (
                selected_patient.get("patient_id")
            )

        # -----------------------------------
        # Restore doctor context
        # -----------------------------------

        if selected_doctor:

            appointment_data["doctor_id"] = (
                selected_doctor.get("doctor_id")
            )

        # -----------------------------------
        # Restore symptom/reason
        # -----------------------------------

        if request_data.get("symptom"):

            appointment_data.setdefault(
                "symptoms",
                request_data.get("symptom")
            )

        # -----------------------------------
        # Restore appointment date
        # -----------------------------------

        if not appointment_data.get(
            "appointment_date"
        ):

            appointment_date = (
                parse_date_from_text(
                    user_input
                )
            )

            if appointment_date:

                appointment_data[
                    "appointment_date"
                ] = appointment_date

        # -----------------------------------
        # Direct booking
        #
        # Example:
        # I want to book Dr Ritu Shah
        # for Friday
        # -----------------------------------

        if is_direct_booking(user_input):

            appointment_data[
                "booking_confirmed"
            ] = True

        # -----------------------------------
        # Appointment doctor selection
        # -----------------------------------

        if awaiting_input == "appointment_doctor":

            doctor_name = user_input

        else:

            doctor_name = (
                request_data.get(
                    "doctor_name",
                    ""
                )
            ).strip()

        # -----------------------------------
        # Doctor selection from list
        # -----------------------------------

        if (
            awaiting_input
            == "appointment_doctor_selection"
        ):

            doctors = (
                state.get("doctors_found")
                or []
            )

            selected_doctor = (
                parse_doctor_selection(
                    user_input,
                    doctors
                )
            )

            if selected_doctor is None:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_doctor_selection"
                )

                state["response"] = (
                    "I couldn't identify the doctor. "
                    "Please enter the number or name "
                    "of the doctor."
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            state["selected_doctor"] = (
                selected_doctor
            )

            appointment_data[
                "doctor_id"
            ] = selected_doctor.get(
                "doctor_id"
            )

        # -----------------------------------
        # Find doctor
        # -----------------------------------

        elif (
            awaiting_input
            == "appointment_doctor"
            or (
                doctor_name
                and not appointment_data.get(
                    "doctor_id"
                )
            )
        ):

            result = (
                DoctorTool.find_doctors_by_name(
                    doctor_name
                )
            )

            doctors = result.get(
                "doctors",
                []
            )

            if not doctors:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_doctor"
                )

                state["response"] = (
                    "I couldn't find that doctor. "
                    "Please enter the doctor's name again."
                )

                state[
                    "appointment_data"
                ] = appointment_data

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

                state["doctors_found"] = (
                    doctors
                )

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_doctor_selection"
                )

                state["response"] = (
                    "I found multiple doctors:\n\n"
                    + "\n".join(doctor_list)
                    + "\n\nWhich doctor do you mean?"
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            selected_doctor = doctors[0]

            state["selected_doctor"] = (
                selected_doctor
            )

            appointment_data[
                "doctor_id"
            ] = selected_doctor.get(
                "doctor_id"
            )

        # -----------------------------------
        # Appointment date input
        # -----------------------------------

        elif awaiting_input == "appointment_date":

            appointment_date = (
                parse_appointment_date(
                    user_input
                )
            )

            if appointment_date is None:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_date"
                )

                state["response"] = (
                    "Please enter a valid appointment "
                    "date such as today, tomorrow, "
                    "Monday, or 2026-08-25."
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            appointment_data[
                "appointment_date"
            ] = appointment_date

        # -----------------------------------
        # Booking confirmation
        #
        # Supports:
        #
        # yes
        # yes 2
        # sure 2
        # book 2
        # -----------------------------------

        elif awaiting_input == "booking_confirmation":

            confirmation = (
                parse_booking_confirmation_with_slot(
                    user_input
                )
            )

            if confirmation is None:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "booking_confirmation"
                )

                state["response"] = (
                    "Please reply yes if you'd like "
                    "to book an appointment, or no if not."
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            confirmed = confirmation[
                "confirmed"
            ]

            if not confirmed:

                state["current_agent"] = None

                state["awaiting_input"] = None

                state["next_step"] = None

                state[
                    "appointment_data"
                ] = {}

                state["response"] = (
                    "No problem. I won't book an appointment."
                )

                return state

            # --------------------------------
            # Booking confirmed
            # --------------------------------

            appointment_data[
                "booking_confirmed"
            ] = True

            # --------------------------------
            # Preserve slot from:
            #
            # Yes 2
            # --------------------------------

            slot_number = confirmation.get(
                "slot_number"
            )

            if slot_number is not None:

                slots = (
                    appointment_data.get(
                        "available_slots",
                        []
                    )
                )

                selected_slot = (
                    parse_slot_selection(
                        str(slot_number),
                        slots
                    )
                )

                if selected_slot is None:

                    state["current_agent"] = (
                        "Appointment"
                    )

                    state["awaiting_input"] = (
                        "appointment_slot_selection"
                    )

                    state["response"] = (
                        "That slot number is not valid. "
                        "Please select one of the available "
                        "slot numbers."
                    )

                    state[
                        "appointment_data"
                    ] = appointment_data

                    return state

                appointment_data[
                    "slot_id"
                ] = selected_slot.get(
                    "slot_id"
                )

                appointment_data[
                    "appointment_time"
                ] = format_slot_time(
                    selected_slot
                )

        # -----------------------------------
        # Appointment slot selection
        # -----------------------------------

        elif (
            awaiting_input
            == "appointment_slot_selection"
        ):

            slots = (
                appointment_data.get(
                    "available_slots",
                    []
                )
            )

            selected_slot = (
                parse_slot_selection(
                    user_input,
                    slots
                )
            )

            if selected_slot is None:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_slot_selection"
                )

                state["response"] = (
                    "Please select a slot by entering "
                    "its number."
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            appointment_data[
                "slot_id"
            ] = selected_slot.get(
                "slot_id"
            )

            appointment_data[
                "appointment_time"
            ] = format_slot_time(
                selected_slot
            )

        # -----------------------------------
        # Symptoms input
        # -----------------------------------

        elif (
            awaiting_input
            == "appointment_symptoms"
        ):

            appointment_data[
                "symptoms"
            ] = user_input

        # -----------------------------------
        # Doctor required
        # -----------------------------------

        if not appointment_data.get(
            "doctor_id"
        ):

            state["current_agent"] = (
                "Appointment"
            )

            state["awaiting_input"] = (
                "appointment_doctor"
            )

            state["response"] = (
                "Which doctor would you like to book?"
            )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Date required
        # -----------------------------------

        if not appointment_data.get(
            "appointment_date"
        ):

            for days_ahead in range(5):

                appointment_date = (
                    date.today()
                    + timedelta(
                        days=days_ahead
                    )
                ).isoformat()

                result = (
                    AppointmentTool
                    .find_available_slots_by_doctor_and_date(
                        appointment_data[
                            "doctor_id"
                        ],
                        appointment_date
                    )
                )

                slots = result.get(
                    "slots",
                    []
                )

                if slots:

                    appointment_data[
                        "appointment_date"
                    ] = appointment_date

                    appointment_data[
                        "available_slots"
                    ] = slots

                    break

            if not appointment_data.get(
                "appointment_date"
            ):

                state["current_agent"] = None

                state["awaiting_input"] = None

                state["next_step"] = None

                state["response"] = (
                    "I couldn't find available slots "
                    "for this doctor right now."
                )

                state[
                    "appointment_data"
                ] = {}

                return state

        # -----------------------------------
        # Booking confirmation / slot
        # -----------------------------------

        if (
            appointment_data.get(
                "booking_confirmed"
            )
            and not appointment_data.get(
                "patient_id"
            )
        ):

            state["current_agent"] = (
                "Appointment"
            )

            state["awaiting_input"] = None

            state["next_step"] = (
                "reception"
            )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Get available slots
        # -----------------------------------

        if not appointment_data.get(
            "appointment_time"
        ):

            if not appointment_data.get(
                "available_slots"
            ):

                result = (
                    AppointmentTool
                    .find_available_slots_by_doctor_and_date(
                        appointment_data[
                            "doctor_id"
                        ],
                        appointment_data[
                            "appointment_date"
                        ]
                    )
                )

                slots = result.get(
                    "slots",
                    []
                )

            else:

                slots = appointment_data.get(
                    "available_slots",
                    []
                )

            if not slots:

                state["current_agent"] = (
                    "Appointment"
                )

                state["awaiting_input"] = (
                    "appointment_date"
                )

                state["response"] = (
                    "I couldn't find available slots "
                    "for that date. Please choose another date."
                )

                state[
                    "appointment_data"
                ] = appointment_data

                return state

            appointment_data[
                "available_slots"
            ] = slots

            slot_list = []

            for index, slot in enumerate(
                slots,
                start=1
            ):

                slot_list.append(
                    f"{index}. "
                    f"{format_slot_time(slot)}"
                )

            state["current_agent"] = (
                "Appointment"
            )

            # --------------------------------
            # Direct booking / confirmed
            # --------------------------------

            if appointment_data.get(
                "booking_confirmed"
            ):

                state["awaiting_input"] = (
                    "appointment_slot_selection"
                )

                state["response"] = (
                    "Available slots for "
                    f"{appointment_data['appointment_date']}:\n\n"
                    + "\n".join(slot_list)
                    + "\n\nPlease select a slot number."
                )

            # --------------------------------
            # Availability preview
            # --------------------------------

            else:

                state["awaiting_input"] = (
                    "booking_confirmation"
                )

                state["response"] = (
                    "Available slots for "
                    f"{appointment_data['appointment_date']}:\n\n"
                    + "\n".join(slot_list)
                    + "\n\nWould you like to book an appointment?"
                )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Booking confirmation still required
        # -----------------------------------

        if not appointment_data.get(
            "booking_confirmed"
        ):

            state["current_agent"] = (
                "Appointment"
            )

            state["awaiting_input"] = (
                "booking_confirmation"
            )

            state["response"] = (
                "Would you like to book an appointment?"
            )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Symptoms required
        # -----------------------------------

        if not appointment_data.get(
            "symptoms"
        ):

            state["current_agent"] = (
                "Appointment"
            )

            state["awaiting_input"] = (
                "appointment_symptoms"
            )

            state["response"] = (
                "Please briefly describe the symptoms "
                "or reason for the visit."
            )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Create Appointment
        # -----------------------------------

        result = (
            AppointmentTool.create_appointment({
                "patient_id": appointment_data[
                    "patient_id"
                ],
                "doctor_id": appointment_data[
                    "doctor_id"
                ],
                "appointment_date": (
                    appointment_data[
                        "appointment_date"
                    ]
                ),
                "appointment_time": (
                    appointment_data[
                        "appointment_time"
                    ]
                ),
                "symptoms": (
                    appointment_data[
                        "symptoms"
                    ]
                )
            })
        )

        state["tool_result"] = result

        # -----------------------------------
        # Booking failed
        # -----------------------------------

        if not result.get("success"):

            appointment_data.pop(
                "appointment_time",
                None
            )

            appointment_data.pop(
                "slot_id",
                None
            )

            state["current_agent"] = (
                "Appointment"
            )

            state["awaiting_input"] = (
                "appointment_slot_selection"
            )

            state["response"] = result.get(
                "message",
                "Appointment could not be booked."
            )

            state[
                "appointment_data"
            ] = appointment_data

            return state

        # -----------------------------------
        # Booking successful
        # -----------------------------------

        state["current_agent"] = None

        state["awaiting_input"] = None

        state["next_step"] = None

        state["appointment_data"] = {}

        state["response"] = result.get(
            "message",
            "Appointment booked successfully"
        )

        return state