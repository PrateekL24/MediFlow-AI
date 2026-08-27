from backend.repositories.doctor_repository import DoctorRepository


class DoctorService:

    @staticmethod
    def get_doctor(doctor_id: str):

        doctor = DoctorRepository.get_doctor(
            doctor_id
        )

        if not doctor:

            return {
                "success": False,
                "message": "Doctor not found"
            }

        return {
            "success": True,
            "data": doctor
        }

    @staticmethod
    def find_doctors_by_name(
        doctor_name: str
    ):

        doctors = (
            DoctorRepository.find_doctors_by_name(
                doctor_name
            )
        )

        return {
            "success": True,
            "count": len(doctors),
            "doctors": doctors
        }

    @staticmethod
    def find_doctors_by_specialization(
        specialization: str
    ):

        doctors = (
            DoctorRepository
            .find_doctors_by_specialization(
                specialization
            )
        )

        return {
            "success": True,
            "count": len(doctors),
            "doctors": doctors
        }

    @staticmethod
    def find_doctors_by_department(
        department_id: str
    ):

        doctors = (
            DoctorRepository
            .find_doctors_by_department(
                department_id
            )
        )

        return {
            "success": True,
            "count": len(doctors),
            "doctors": doctors
        }

    @staticmethod
    def get_all_active_doctors():

        doctors = (
            DoctorRepository
            .get_all_active_doctors()
        )

        return {
            "success": True,
            "count": len(doctors),
            "doctors": doctors
        }