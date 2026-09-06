from backend.repositories.appointment_repository import AppointmentRepository


class AppointmentService:

    @staticmethod
    def validate_required_fields(appointment_data: dict):
        required_fields = [
            "patient_id",
            "doctor_id",
            "slot_id",
            "appointment_date",
            "appointment_time",
            "symptoms"
        ]

        missing_fields = []

        for field in required_fields:
            value = appointment_data.get(field)

            if value is None or value == "":
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def find_available_slots_by_doctor_and_date(
        doctor_id: str,
        appointment_date: str
    ):
        slots = AppointmentRepository.find_available_slots_by_doctor_and_date(
            doctor_id,
            appointment_date
        )

        return {
            "success": True,
            "count": len(slots),
            "slots": slots
        }

    @staticmethod
    def create_appointment(appointment_data: dict):
        appointment_data = dict(appointment_data)

        missing_fields = AppointmentService.validate_required_fields(
            appointment_data
        )

        if missing_fields:
            return {
                "success": False,
                "missing_fields": missing_fields,
                "message": "Missing required appointment information."
            }

        slot_id = appointment_data["slot_id"]

        # Re-check the selected slot immediately before booking.
        slot = AppointmentRepository.get_slot(slot_id)

        if slot is None:
            return {
                "success": False,
                "message": "The selected appointment slot could not be found."
            }

        if slot.get("status") != "available":
            return {
                "success": False,
                "message": (
                    "That appointment slot is no longer available. "
                    "Please choose another slot."
                )
            }

        # Make sure the slot belongs to the requested doctor.
        if slot.get("doctor_id") != appointment_data["doctor_id"]:
            return {
                "success": False,
                "message": "The selected slot does not belong to this doctor."
            }

        slot_start = slot.get("start_time", "")

        if not slot_start:
            return {
                "success": False,
                "message": "The selected appointment slot is invalid."
            }

        # Example database value:
        # 2026-09-07T09:00:00
        #
        # We only need:
        # date -> 2026-09-07
        # time -> 09:00
        slot_date = slot_start[:10]
        slot_time = slot_start[11:16]

        if slot_date != appointment_data["appointment_date"]:
            return {
                "success": False,
                "message": "The selected slot does not match the appointment date."
            }

        if slot_time != appointment_data["appointment_time"]:
            return {
                "success": False,
                "message": "The selected slot does not match the appointment time."
            }

        # Preserve the existing duplicate appointment check.
        existing = AppointmentRepository.find_existing_appointment(
            appointment_data["doctor_id"],
            appointment_data["appointment_date"],
            appointment_data["appointment_time"]
        )

        if existing:
            return {
                "success": False,
                "message": (
                    "That appointment time is already booked. "
                    "Please choose another available slot."
                )
            }

        appointment_data["status"] = "Booked"

        appointment = AppointmentRepository.create_appointment(
            appointment_data
        )

        if not appointment:
            return {
                "success": False,
                "message": "The appointment could not be created."
            }

        slot_update = AppointmentRepository.mark_slot_booked(
            slot_id
        )

        if not slot_update:
            return {
                "success": False,
                "message": (
                    "The appointment was created, but the slot "
                    "could not be marked as booked."
                )
            }

        return {
            "success": True,
            "data": appointment,
            "message": "Appointment booked successfully"
        }