from datetime import date, datetime, timedelta
import re

from backend.tools.appointment_tool import AppointmentTool
from backend.tools.doctor_tool import DoctorTool


def parse_appointment_date(value: str):
    text = value.strip().lower()
    if text == "today":
        return date.today().isoformat()
    if text == "tomorrow":
        return (date.today() + timedelta(days=1)).isoformat()
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    if text in weekdays:
        today = date.today()
        days_ahead = (weekdays[text] - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).isoformat()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None


def parse_date_from_text(value: str):
    words = value.replace(".", " ").replace(",", " ").split()
    for word in words:
        parsed = parse_appointment_date(word)
        if parsed is not None:
            return parsed
    return None


def parse_doctor_selection(value: str, doctors: list):
    text = value.strip().lower()
    if text.isdigit():
        index = int(text) - 1
        if 0 <= index < len(doctors):
            return doctors[index]
        return None
    matches = []
    for doctor in doctors:
        doctor_name = doctor.get("doctor_name", "").strip().lower()
        if doctor_name and doctor_name in text:
            matches.append(doctor)
    return matches[0] if len(matches) == 1 else None


def _normalise_time(value: str):
    text = value.strip().lower().replace(".", "")
    for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
        try:
            return datetime.strptime(text, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


def parse_time_from_text(value: str):
    match = re.search(
        r"\b(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?))\b",
        value,
        re.IGNORECASE,
    )
    if not match:
        match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", value)
    return _normalise_time(match.group(1)) if match else None


def parse_slot_selection(value: str, slots: list):
    text = value.strip()
    if text.isdigit():
        index = int(text) - 1
        return slots[index] if 0 <= index < len(slots) else None

    requested_time = parse_time_from_text(text)
    if requested_time is None:
        return None

    for slot in slots:
        if format_slot_time(slot) == requested_time:
            return slot

    return None


def format_slot_time(slot: dict):
    start_time = slot.get("start_time", "")
    try:
        parsed = datetime.fromisoformat(start_time)
        return parsed.strftime("%H:%M")
    except (ValueError, TypeError):
        return start_time


def parse_confirmation(value: str):
    text = value.strip().lower()
    if text in {"yes", "y", "sure", "ok", "okay", "confirm", "confirmed"}:
        return True
    if text in {"no", "n", "cancel", "not now", "no thanks"}:
        return False
    return None


class AppointmentAgent:
    @staticmethod
    def run(state):
        appointment_data = state.get("appointment_data") or {}
        request_data = state.get("request_data") or {}
        user_input = (state.get("user_input") or "").strip()
        awaiting_input = state.get("awaiting_input")
        selected_patient = state.get("selected_patient")
        selected_doctor = state.get("selected_doctor")
        intent = state.get("intent")

        if selected_patient:
            appointment_data["patient_id"] = selected_patient.get("patient_id")

        if selected_doctor:
            appointment_data["doctor_id"] = selected_doctor.get("doctor_id")

        if request_data.get("symptom"):
            appointment_data.setdefault("symptoms", request_data["symptom"])

        if awaiting_input == "appointment_doctor":
            request_data["doctor_name"] = user_input

        elif awaiting_input == "appointment_doctor_selection":
            doctors = state.get("doctors_found") or []
            selected_doctor = parse_doctor_selection(user_input, doctors)

            if selected_doctor is None:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_doctor_selection"
                state["response"] = (
                    "I couldn't identify the doctor. "
                    "Please enter the number or name of the doctor."
                )
                return state

            state["selected_doctor"] = selected_doctor
            appointment_data["doctor_id"] = selected_doctor.get("doctor_id")
            request_data["doctor_name"] = selected_doctor.get("doctor_name", "")
            state["request_data"] = request_data

        elif awaiting_input == "appointment_date":
            appointment_date = parse_appointment_date(user_input)

            if appointment_date is None:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_date"
                state["response"] = (
                    "Please enter a valid appointment date such as today, "
                    "tomorrow, Monday, or 2026-09-15."
                )
                return state

            appointment_data["appointment_date"] = appointment_date

        elif awaiting_input == "appointment_slot_selection":
            slots = appointment_data.get("available_slots") or []
            selected_slot = parse_slot_selection(user_input, slots)

            if selected_slot is None:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_slot_selection"
                state["response"] = (
                    "Please select an available slot by number or time, "
                    "for example 2 or 10:30 AM."
                )
                return state

            appointment_data["slot_id"] = selected_slot.get("slot_id")
            appointment_data["appointment_time"] = format_slot_time(selected_slot)

            if not appointment_data.get("patient_id"):
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = None
                state["next_step"] = "reception"
                state["appointment_data"] = appointment_data
                state["response"] = (
                    "Great. Before I book that slot, may I have the patient's mobile number?"
                )
                return state

        elif awaiting_input == "appointment_symptoms":
            appointment_data["symptoms"] = user_input

        elif awaiting_input == "booking_confirmation":
            confirmation = parse_confirmation(user_input)

            if confirmation is None:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "booking_confirmation"
                state["response"] = (
                    "Please reply yes to confirm the appointment or no to cancel."
                )
                return state

            if not confirmation:
                state["current_agent"] = None
                state["awaiting_input"] = None
                state["next_step"] = None
                state["appointment_data"] = {}
                state["response"] = "No problem. I won't book the appointment."
                return state

            appointment_data["booking_confirmed"] = True

        doctor_name = (request_data.get("doctor_name") or "").strip()

        if not appointment_data.get("doctor_id"):
            if not doctor_name:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_doctor"
                state["response"] = "Which doctor would you like to book?"
                state["appointment_data"] = appointment_data
                return state

            result = DoctorTool.find_doctors_by_name(doctor_name)
            doctors = result.get("doctors", [])

            if not doctors:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_doctor"
                state["response"] = (
                    f"I couldn't find a doctor matching '{doctor_name}'. "
                    "Please enter the doctor's name again."
                )
                state["appointment_data"] = appointment_data
                return state

            if len(doctors) > 1:
                state["doctors_found"] = doctors
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_doctor_selection"
                state["response"] = (
                    "I found multiple doctors:\n\n"
                    + "\n".join(
                        f"{i}. {d.get('doctor_name', '')}"
                        for i, d in enumerate(doctors, 1)
                    )
                    + "\n\nWhich doctor do you mean?"
                )
                state["appointment_data"] = appointment_data
                return state

            selected_doctor = doctors[0]
            state["selected_doctor"] = selected_doctor
            appointment_data["doctor_id"] = selected_doctor.get("doctor_id")

        if not appointment_data.get("appointment_date"):
            appointment_date = parse_date_from_text(user_input)

            if appointment_date:
                appointment_data["appointment_date"] = appointment_date
            else:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_date"
                state["response"] = "What date would you like the appointment?"
                state["appointment_data"] = appointment_data
                return state

        if not appointment_data.get("available_slots"):
            result = AppointmentTool.find_available_slots_by_doctor_and_date(
                appointment_data["doctor_id"],
                appointment_data["appointment_date"],
            )
            slots = result.get("slots", [])

            if not slots:
                state["current_agent"] = "Appointment"
                state["awaiting_input"] = "appointment_date"
                state["response"] = (
                    "I couldn't find available slots for that date. "
                    "Please choose another date."
                )
                state["appointment_data"] = appointment_data
                return state

            appointment_data["available_slots"] = slots

        # Resolve an exact time supplied in the original request now that
        # actual slots have been loaded.
        if not appointment_data.get("appointment_time"):
            requested_time = parse_time_from_text(user_input)

            if requested_time:
                selected_slot = next(
                    (
                        slot
                        for slot in appointment_data["available_slots"]
                        if format_slot_time(slot) == requested_time
                    ),
                    None,
                )

                if selected_slot:
                    appointment_data["slot_id"] = selected_slot.get("slot_id")
                    appointment_data["appointment_time"] = format_slot_time(
                        selected_slot
                    )
                elif intent == "book_appointment":
                    slot_list = "\n".join(
                        f"{i}. {format_slot_time(slot)}"
                        for i, slot in enumerate(
                            appointment_data["available_slots"],
                            1,
                        )
                    )
                    state["current_agent"] = "Appointment"
                    state["awaiting_input"] = "appointment_slot_selection"
                    state["appointment_data"] = appointment_data
                    state["response"] = (
                        f"The {requested_time} slot is not available. "
                        "Please choose one of these available slots:\n\n"
                        + slot_list
                    )
                    return state

        if not appointment_data.get("appointment_time"):
            slot_list = "\n".join(
                f"{i}. {format_slot_time(slot)}"
                for i, slot in enumerate(
                    appointment_data["available_slots"],
                    1,
                )
            )

            state["current_agent"] = "Appointment"
            state["appointment_data"] = appointment_data

            if intent == "book_appointment":
                state["awaiting_input"] = "appointment_slot_selection"
                state["response"] = (
                    f"Available slots for {appointment_data['appointment_date']}:\n\n"
                    + slot_list
                    + "\n\nPlease select a slot by number or time."
                )
            else:
                state["awaiting_input"] = None
                state["next_step"] = None
                state["response"] = (
                    f"Available slots for {appointment_data['appointment_date']}:\n\n"
                    + slot_list
                )

            return state

        if not appointment_data.get("patient_id"):
            state["current_agent"] = "Appointment"
            state["awaiting_input"] = None
            state["next_step"] = "reception"
            state["appointment_data"] = appointment_data
            state["response"] = (
                "Before I book that slot, may I have the patient's mobile number?"
            )
            return state

        if not appointment_data.get("symptoms"):
            state["current_agent"] = "Appointment"
            state["awaiting_input"] = "appointment_symptoms"
            state["appointment_data"] = appointment_data
            state["response"] = (
                "Please briefly describe the symptoms or reason for the visit."
            )
            return state

        if not appointment_data.get("booking_confirmed"):
            doctor_label = (
                (state.get("selected_doctor") or {}).get("doctor_name")
                or doctor_name
            )
            patient_label = (
                (state.get("selected_patient") or {}).get("first_name")
                or "the patient"
            )

            state["current_agent"] = "Appointment"
            state["awaiting_input"] = "booking_confirmation"
            state["appointment_data"] = appointment_data
            state["response"] = (
                "Please confirm:\n\n"
                f"Doctor: {doctor_label}\n"
                f"Date: {appointment_data['appointment_date']}\n"
                f"Time: {appointment_data['appointment_time']}\n"
                f"Patient: {patient_label}\n\n"
                "Would you like me to confirm this appointment?"
            )
            return state

        # Re-check availability immediately before creating the appointment.
        result = AppointmentTool.find_available_slots_by_doctor_and_date(
            appointment_data["doctor_id"],
            appointment_data["appointment_date"],
        )
        current_slots = result.get("slots", [])
        requested_time = appointment_data["appointment_time"]

        if not any(
            format_slot_time(slot) == requested_time
            for slot in current_slots
        ):
            appointment_data.pop("appointment_time", None)
            appointment_data.pop("slot_id", None)
            appointment_data.pop("booking_confirmed", None)
            appointment_data["available_slots"] = current_slots

            state["current_agent"] = "Appointment"
            state["awaiting_input"] = "appointment_slot_selection"
            state["appointment_data"] = appointment_data

            if not current_slots:
                state["response"] = (
                    "That slot is no longer available, and there are no other slots "
                    "on that date. Please choose another date."
                )
            else:
                slot_list = "\n".join(
                    f"{i}. {format_slot_time(slot)}"
                    for i, slot in enumerate(current_slots, 1)
                )
                state["response"] = (
                    "That slot is no longer available. Please choose another slot:\n\n"
                    + slot_list
                )

            return state

        result = AppointmentTool.create_appointment(
            {
                "patient_id": appointment_data["patient_id"],
                "doctor_id": appointment_data["doctor_id"],
                "appointment_date": appointment_data["appointment_date"],
                "appointment_time": appointment_data["appointment_time"],
                "symptoms": appointment_data["symptoms"],
            }
        )
        state["tool_result"] = result

        if not result.get("success"):
            appointment_data.pop("appointment_time", None)
            appointment_data.pop("slot_id", None)
            appointment_data.pop("booking_confirmed", None)
            state["current_agent"] = "Appointment"
            state["awaiting_input"] = "appointment_slot_selection"
            state["appointment_data"] = appointment_data
            state["response"] = result.get(
                "message",
                "Appointment could not be booked. Please choose another slot.",
            )
            return state

        state["current_agent"] = None
        state["awaiting_input"] = None
        state["next_step"] = None
        state["appointment_data"] = {}
        state["response"] = result.get(
            "message",
            "Appointment booked successfully",
        )
        return state
