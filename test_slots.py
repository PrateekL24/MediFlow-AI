from backend.tools.doctor_tool import DoctorTool
from backend.tools.appointment_tool import AppointmentTool


print("\n===== DOCTOR =====")

result = DoctorTool.find_doctors_by_name("Dr. Ritu Shah")
print(result)

doctor = result["doctors"][0]
doctor_id = doctor["doctor_id"]

print("\nDoctor ID:")
print(doctor_id)


print("\n===== NEXT 5 DAYS =====")

from datetime import date, timedelta

for i in range(5):

    d = date.today() + timedelta(days=i)

    result = AppointmentTool.find_available_slots_by_doctor_and_date(
        doctor_id,
        d.isoformat()
    )

    slots = result.get("slots", [])

    print(
        d.isoformat(),
        "=>",
        len(slots),
        "slots"
    )