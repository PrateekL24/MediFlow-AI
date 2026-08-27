from backend.core.database import supabase


class DoctorRepository:

    @staticmethod
    def get_doctor(doctor_id: str):

        response = (
            supabase
            .table("doctors")
            .select("*")
            .eq("doctor_id", doctor_id)
            .single()
            .execute()
        )

        return response.data

    @staticmethod
    def find_doctors_by_name(doctor_name: str):

        response = (
            supabase
            .table("doctors")
            .select("*")
            .ilike("doctor_name", f"%{doctor_name}%")
            .execute()
        )

        return response.data

    @staticmethod
    def find_doctors_by_specialization(
        specialization: str
    ):

        response = (
            supabase
            .table("doctors")
            .select("*")
            .ilike(
                "specialization",
                f"%{specialization}%"
            )
            .eq("status", "Available")
            .execute()
        )

        return response.data

    @staticmethod
    def find_doctors_by_department(
        department_id: str
    ):

        response = (
            supabase
            .table("doctors")
            .select("*")
            .eq("department_id", department_id)
            .eq("status", "Available")
            .execute()
        )

        return response.data

    @staticmethod
    def get_all_active_doctors():

        response = (
            supabase
            .table("doctors")
            .select("*")
            .eq("status", "Available")
            .execute()
        )

        return response.data