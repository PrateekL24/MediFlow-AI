from backend.repositories.patient_repository import PatientRepository


class PatientService:

    @staticmethod
    def validate_required_fields(patient_data: dict):

        required_fields = [
            "first_name",
            "age",
            "phone"
        ]

        missing_fields = []

        for field in required_fields:

            value = patient_data.get(field)

            if value is None or value == "":
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def create_patient(patient_data: dict):

        missing_fields = PatientService.validate_required_fields(patient_data)

        if missing_fields:
            return {
                "success": False,
                "missing_fields": missing_fields,
                "message": "Missing required information."
            }

        patient = PatientRepository.create_patient(patient_data)

        return {
            "success": True,
            "data": patient,
            "message": "Patient created successfully"
        }

    @staticmethod
    def get_patient(patient_id: str):

        patient = PatientRepository.get_patient(patient_id)

        if not patient:
            return {
                "success": False,
                "message": "Patient not found"
            }

        return {
            "success": True,
            "data": patient
        }

    @staticmethod
    def find_patients_by_phone(phone: str):

        patients = PatientRepository.find_patients_by_phone(phone)

        if not patients:

            return {
                "success": True,
                "count": 0,
                "patients": []
            }

        return {
            "success": True,
            "count": len(patients),
            "patients": patients
        }

    @staticmethod
    def update_patient(patient_id: str, patient_data: dict):

        patient = PatientRepository.update_patient(
            patient_id,
            patient_data
        )

        return {
            "success": True,
            "data": patient,
            "message": "Patient updated successfully"
        }

    @staticmethod
    def delete_patient(patient_id: str):

        PatientRepository.delete_patient(patient_id)

        return {
            "success": True,
            "message": "Patient deleted successfully"
        }