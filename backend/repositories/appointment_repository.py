from datetime import datetime, timedelta

from backend.core.database import supabase


class AppointmentRepository:

    @staticmethod
    def find_available_slots_by_doctor_and_date(
        doctor_id: str,
        appointment_date: str
    ):
        start_date = datetime.fromisoformat(appointment_date)
        next_date = start_date + timedelta(days=1)

        response = (
            supabase.table("appointment_slots")
            .select("*")
            .eq("doctor_id", doctor_id)
            .eq("status", "available")
            .gte("start_time", start_date.isoformat())
            .lt("start_time", next_date.isoformat())
            .order("start_time")
            .execute()
        )

        return response.data

    @staticmethod
    def get_slot(slot_id: str):
        response = (
            supabase.table("appointment_slots")
            .select("*")
            .eq("slot_id", slot_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    @staticmethod
    def mark_slot_booked(slot_id: str):
        response = (
            supabase.table("appointment_slots")
            .update({"status": "booked"})
            .eq("slot_id", slot_id)
            .eq("status", "available")
            .execute()
        )

        return response.data

    @staticmethod
    def find_existing_appointment(
        doctor_id: str,
        appointment_date: str,
        appointment_time: str
    ):
        response = (
            supabase.table("appointments")
            .select("*")
            .eq("doctor_id", doctor_id)
            .eq("appointment_date", appointment_date)
            .eq("appointment_time", appointment_time)
            .execute()
        )

        return response.data

    @staticmethod
    def create_appointment(appointment_data: dict):
        response = (
            supabase.table("appointments")
            .insert(appointment_data)
            .execute()
        )

        return response.data