from backend.repositories.audit_repository import AuditRepository
from backend.services.appointment_service import AppointmentService


def test_audit_repository_inserts_expected_payload(monkeypatch):
    captured = {}

    class FakeResponse:
        data = [{"audit_id": "audit-1"}]

    class FakeTable:
        def insert(self, payload):
            captured["payload"] = payload
            return self

        def execute(self):
            return FakeResponse()

    class FakeSupabase:
        def table(self, name):
            captured["table"] = name
            return FakeTable()

    monkeypatch.setattr(
        "backend.repositories.audit_repository.supabase",
        FakeSupabase()
    )

    result = AuditRepository.create_event(
        workflow_id="workflow-1",
        agent_name="Appointment",
        tool_name="AppointmentTool",
        action="appointment_booking",
        status="success",
        metadata={"reason": "booking_created"},
    )

    assert result == [{"audit_id": "audit-1"}]
    assert captured["table"] == "audit_events"
    assert captured["payload"] == {
        "workflow_id": "workflow-1",
        "agent_name": "Appointment",
        "tool_name": "AppointmentTool",
        "action": "appointment_booking",
        "status": "success",
        "metadata": {"reason": "booking_created"},
    }


def test_appointment_booking_success_creates_audit_event(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        "backend.services.appointment_service.AppointmentRepository.book_appointment",
        lambda **kwargs: [{"appointment_id": "appointment-1"}],
    )

    def fake_audit(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "backend.services.appointment_service.AuditService.record_event",
        fake_audit,
    )

    result = AppointmentService.create_appointment({
        "_workflow_id": "workflow-1",
        "patient_id": "patient-1",
        "doctor_id": "doctor-1",
        "slot_id": "slot-1",
        "appointment_date": "2026-09-10",
        "appointment_time": "10:30",
        "symptoms": "back pain",
    })

    assert result["success"] is True
    assert captured["workflow_id"] == "workflow-1"
    assert captured["agent_name"] == "Appointment"
    assert captured["tool_name"] == "AppointmentTool"
    assert captured["action"] == "appointment_booking"
    assert captured["status"] == "success"
    assert captured["metadata"] == {"reason": "booking_created"}


def test_appointment_booking_failure_creates_audit_event(monkeypatch):
    captured = {}

    def fake_booking(**kwargs):
        raise Exception("APPOINTMENT_SLOT_NOT_AVAILABLE")

    monkeypatch.setattr(
        "backend.services.appointment_service.AppointmentRepository.book_appointment",
        fake_booking,
    )

    def fake_audit(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "backend.services.appointment_service.AuditService.record_event",
        fake_audit,
    )

    result = AppointmentService.create_appointment({
        "_workflow_id": "workflow-1",
        "patient_id": "patient-1",
        "doctor_id": "doctor-1",
        "slot_id": "slot-1",
        "appointment_date": "2026-09-10",
        "appointment_time": "10:30",
        "symptoms": "back pain",
    })

    assert result["success"] is False
    assert "no longer available" in result["message"]
    assert captured["workflow_id"] == "workflow-1"
    assert captured["status"] == "failure"
    assert captured["metadata"] == {"reason": "slot_not_available"}
