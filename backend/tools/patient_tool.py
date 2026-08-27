from backend.services.patient_service import PatientService


class PatientTool:

    @staticmethod
    def create_patient(patient_data: dict):

        return PatientService.create_patient(patient_data)

    @staticmethod
    def get_patient(patient_id: str):

        return PatientService.get_patient(patient_id)

    @staticmethod
    def find_patients_by_phone(phone: str):

        return PatientService.find_patients_by_phone(phone)

    @staticmethod
    def update_patient(patient_id: str, patient_data: dict):

        return PatientService.update_patient(
            patient_id,
            patient_data
        )

    @staticmethod
    def delete_patient(patient_id: str):

        return PatientService.delete_patient(patient_id)