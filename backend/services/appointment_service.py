from backend.repositories.appointment_repository import AppointmentRepository
from backend.services.audit_service import AuditService


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
    def _audit_booking(
        workflow_id: str | None,
        status: str,
        metadata: dict | None = None,
    ):
        AuditService.record_event(
            workflow_id=workflow_id,
            agent_name="Appointment",
            tool_name="AppointmentTool",
            action="appointment_booking",
            status=status,
            metadata=metadata or {},
        )

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

        # Internal workflow context used only for audit correlation.
        # It is removed before any appointment repository call.
        workflow_id = appointment_data.pop("_workflow_id", None)

        missing_fields = AppointmentService.validate_required_fields(
            appointment_data
        )

        if missing_fields:
            AppointmentService._audit_booking(
                workflow_id=workflow_id,
                status="failure",
                metadata={
                    "reason": "missing_required_fields",
                    "missing_field_count": len(missing_fields),
                },
            )

            return {
                "success": False,
                "missing_fields": missing_fields,
                "message": "Missing required appointment information."
            }

        try:
            appointment = AppointmentRepository.book_appointment(
                patient_id=appointment_data["patient_id"],
                doctor_id=appointment_data["doctor_id"],
                slot_id=appointment_data["slot_id"],
                appointment_date=appointment_data["appointment_date"],
                appointment_time=appointment_data["appointment_time"],
                symptoms=appointment_data["symptoms"]
            )

        except Exception as exc:
            error_message = str(exc)

            if "APPOINTMENT_SLOT_NOT_FOUND" in error_message:
                message = (
                    "The selected appointment slot could not be found."
                )
                reason = "slot_not_found"

            elif "APPOINTMENT_SLOT_NOT_AVAILABLE" in error_message:
                message = (
                    "That appointment slot is no longer available. "
                    "Please choose another available slot."
                )
                reason = "slot_not_available"

            elif "SLOT_DOCTOR_MISMATCH" in error_message:
                message = (
                    "The selected slot does not belong to this doctor."
                )
                reason = "slot_doctor_mismatch"

            elif "SLOT_DATE_MISMATCH" in error_message:
                message = (
                    "The selected slot does not match the appointment date."
                )
                reason = "slot_date_mismatch"

            elif "SLOT_TIME_MISMATCH" in error_message:
                message = (
                    "The selected slot does not match the appointment time."
                )
                reason = "slot_time_mismatch"

            else:
                message = "The appointment could not be booked."
                reason = "booking_error"

            AppointmentService._audit_booking(
                workflow_id=workflow_id,
                status="failure",
                metadata={"reason": reason},
            )

            return {
                "success": False,
                "message": message
            }

        if not appointment:
            AppointmentService._audit_booking(
                workflow_id=workflow_id,
                status="failure",
                metadata={"reason": "empty_booking_result"},
            )

            return {
                "success": False,
                "message": "The appointment could not be booked."
            }

        AppointmentService._audit_booking(
            workflow_id=workflow_id,
            status="success",
            metadata={"reason": "booking_created"},
        )

        return {
            "success": True,
            "data": appointment,
            "message": "Appointment booked successfully"
        }
