from backend.core.database import supabase


class PatientRepository:

    @staticmethod
    def create_patient(patient_data: dict):
        response = (
            supabase
            .table("patients")
            .insert(patient_data)
            .execute()
        )

        return response.data

    @staticmethod
    def get_patient(patient_id: str):
        response = (
            supabase
            .table("patients")
            .select("*")
            .eq("patient_id", patient_id)
            .single()
            .execute()
        )

        return response.data

    @staticmethod
    def find_patients_by_phone(phone: str):
        """
        Returns ALL patients linked with the given phone number.
        """

        response = (
            supabase
            .table("patients")
            .select("*")
            .eq("phone", phone)
            .execute()
        )

        return response.data

    @staticmethod
    def update_patient(patient_id: str, patient_data: dict):
        response = (
            supabase
            .table("patients")
            .update(patient_data)
            .eq("patient_id", patient_id)
            .execute()
        )

        return response.data

    @staticmethod
    def delete_patient(patient_id: str):
        response = (
            supabase
            .table("patients")
            .delete()
            .eq("patient_id", patient_id)
            .execute()
        )

        return response.data