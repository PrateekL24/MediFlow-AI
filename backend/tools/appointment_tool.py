from backend.services.appointment_service import AppointmentService


class AppointmentTool:

    @staticmethod
    def find_available_slots_by_doctor_and_date(
        doctor_id: str,
        appointment_date: str
    ):

        return (
            AppointmentService
            .find_available_slots_by_doctor_and_date(
                doctor_id,
                appointment_date
            )
        )

    @staticmethod
    def create_appointment(appointment_data: dict):

        return AppointmentService.create_appointment(
            appointment_data
        )
