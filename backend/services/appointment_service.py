from backend.repositories.appointment_repository import AppointmentRepository


class AppointmentService:

    @staticmethod
    def validate_required_fields(appointment_data: dict):

        required_fields = [
            "patient_id",
            "doctor_id",
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

        slots = (
            AppointmentRepository
            .find_available_slots_by_doctor_and_date(
                doctor_id,
                appointment_date
            )
        )

        return {
            "success": True,
            "count": len(slots),
            "slots": slots
        }

    @staticmethod
    def create_appointment(appointment_data: dict):

        appointment_data = dict(appointment_data)
        appointment_data["status"] = "Booked"

        missing_fields = (
            AppointmentService
            .validate_required_fields(appointment_data)
        )

        if missing_fields:

            return {
                "success": False,
                "missing_fields": missing_fields,
                "message": "Missing required appointment information."
            }

        existing = (
            AppointmentRepository
            .find_existing_appointment(
                appointment_data["doctor_id"],
                appointment_data["appointment_date"],
                appointment_data["appointment_time"]
            )
        )

        if existing:

            return {
                "success": False,
                "message": (
                    "That appointment time is already booked. "
                    "Please choose another available slot."
                )
            }

        appointment = (
            AppointmentRepository
            .create_appointment(appointment_data)
        )

        return {
            "success": True,
            "data": appointment,
            "message": "Appointment booked successfully"
        }
