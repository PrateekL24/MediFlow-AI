from backend.services.doctor_service import DoctorService


class DoctorTool:

    @staticmethod
    def get_doctor(doctor_id: str):

        return DoctorService.get_doctor(
            doctor_id
        )

    @staticmethod
    def find_doctors_by_name(
        doctor_name: str
    ):

        return DoctorService.find_doctors_by_name(
            doctor_name
        )

    @staticmethod
    def find_doctors_by_specialization(
        specialization: str
    ):

        return DoctorService.find_doctors_by_specialization(
            specialization
        )

    @staticmethod
    def find_doctors_by_department(
        department_id: str
    ):

        return DoctorService.find_doctors_by_department(
            department_id
        )

    @staticmethod
    def get_all_active_doctors():

        return DoctorService.get_all_active_doctors()