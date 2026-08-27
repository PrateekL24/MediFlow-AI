from supabase import create_client
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import os
import hashlib

# --------------------------------------------------
# Load Environment
# --------------------------------------------------

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

fake = Faker("en_IN")

# --------------------------------------------------
# Global Lists
# --------------------------------------------------

user_ids = []
doctor_ids = []
patient_ids = []
appointment_ids = []
workflow_ids = []
slot_ids = []

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def random_datetime(days=30):
    return (
        datetime.now()
        + timedelta(
            days=random.randint(1, days),
            hours=random.randint(8, 17)
        )
    )


def checksum():
    return hashlib.md5(
        fake.uuid4().encode()
    ).hexdigest()


def print_header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
# --------------------------------------------------
# Seed Users
# --------------------------------------------------

def seed_users():

    print_header("Seeding Users")

    for _ in range(5):

        user = supabase.table("users").insert({
            "full_name": fake.name(),
            "email": fake.unique.email(),
            "role": random.choice(["staff", "admin"])
        }).execute()

        user_ids.append(user.data[0]["id"])

    print(f"✅ {len(user_ids)} Users Created")


# --------------------------------------------------
# Seed Doctors
# --------------------------------------------------

def seed_doctors():

    print_header("Seeding Doctors")

    departments = supabase.table("departments").select("*").execute().data

    department_map = {
        d["department_name"]: d["department_id"]
        for d in departments
    }

    doctor_names = [
        "Dr. Amit Sharma",
        "Dr. Priya Singh",
        "Dr. Rahul Verma",
        "Dr. Sneha Patel",
        "Dr. Karan Mehta",
        "Dr. Neha Kapoor",
        "Dr. Arjun Nair",
        "Dr. Vivek Joshi",
        "Dr. Pooja Rao",
        "Dr. Ritu Shah",
        "Dr. Ankit Jain",
        "Dr. Sonia Gupta",
        "Dr. Mohit Kulkarni",
        "Dr. Kavita Das",
        "Dr. Rohit Bansal"
    ]

    department_names = list(department_map.keys())

    for doctor_name in doctor_names:

        department = random.choice(department_names)

        doctor = supabase.table("doctors").insert({

            "doctor_name": doctor_name,
            "department_id": department_map[department],
            "specialization": department,
            "experience_years": random.randint(3, 25),
            "available_days": "Mon,Tue,Wed,Thu,Fri",
            "available_time": "09:00 AM - 05:00 PM",
            "consultation_fee": random.choice([500,700,900,1200]),
            "status": "Available"

        }).execute()

        doctor_ids.append(doctor.data[0]["doctor_id"])

    print(f"✅ {len(doctor_ids)} Doctors Created")

# --------------------------------------------------
# Seed Patients
# --------------------------------------------------

def seed_patients():

    print_header("Seeding Patients")

    for _ in range(50):

        patient = supabase.table("patients").insert({

            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "gender": random.choice(["Male", "Female"]),
            "age": random.randint(18, 80),
            "blood_group": random.choice([
                "A+","B+","AB+","O+",
                "A-","B-","AB-","O-"
            ]),
            "phone": fake.phone_number(),
            "email": fake.unique.email(),
            "address": fake.address()

        }).execute()

        patient_ids.append(patient.data[0]["patient_id"])

    print(f"✅ {len(patient_ids)} Patients Created")


# --------------------------------------------------
# Seed Appointment Slots
# --------------------------------------------------

def seed_appointment_slots():

    print_header("Seeding Appointment Slots")

    base_date = datetime.now().replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0
    )

    for doctor_id in doctor_ids:

        for day in range(5):          # Next 5 days

            current_day = base_date + timedelta(days=day)

            for hour in range(9, 17): # 9 AM - 5 PM

                start = current_day.replace(hour=hour)
                end = start + timedelta(hours=1)

                slot = supabase.table("appointment_slots").insert({

                    "doctor_id": doctor_id,
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "status": "available"

                }).execute()

                slot_ids.append(slot.data[0]["slot_id"])

    print(f"✅ {len(slot_ids)} Appointment Slots Created")

# --------------------------------------------------
# Seed Appointments
# --------------------------------------------------

def seed_appointments():

    print_header("Seeding Appointments")

    statuses = ["Booked", "Completed", "Cancelled"]

    for _ in range(100):

        appointment_date = random_datetime(30)

        appointment = supabase.table("appointments").insert({

            "patient_id": random.choice(patient_ids),
            "doctor_id": random.choice(doctor_ids),
            "appointment_date": appointment_date.date().isoformat(),
            "appointment_time": appointment_date.strftime("%H:%M"),
            "symptoms": fake.sentence(nb_words=8),
            "status": random.choice(statuses)

        }).execute()

        appointment_ids.append(
            appointment.data[0]["appointment_id"]
        )

    print(f"✅ {len(appointment_ids)} Appointments Created")


# --------------------------------------------------
# Seed Documents
# --------------------------------------------------

def seed_documents():

    print_header("Seeding Documents")

    document_names = [
        "Blood Report",
        "MRI Scan",
        "X-Ray",
        "Prescription",
        "ECG Report",
        "CT Scan",
        "Urine Report"
    ]

    for _ in range(30):

        doc_name = random.choice(document_names)

        supabase.table("documents").insert({

            "patient_id": random.choice(patient_ids),

            "document_name": doc_name,

            "document_type": "PDF",

            "file_path": f"uploads/{fake.uuid4()}.pdf",

            # Ignore these two lines if your documents table
            # doesn't have these columns yet.
            # "checksum": checksum(),
            # "storage_url": f"https://storage.supabase.co/{fake.uuid4()}.pdf"

        }).execute()

    print("✅ 30 Documents Created")

# --------------------------------------------------
# Seed Workflow Runs
# --------------------------------------------------

def seed_workflows():

    print_header("Seeding Workflow Runs")

    agents = [
        "Supervisor",
        "Registration",
        "Appointment",
        "Document",
        "FollowUp"
    ]

    for _ in range(10):

        workflow = supabase.table("workflow_runs").insert({

            "session_id": fake.uuid4(),

            "current_agent": random.choice(agents),

            "current_node": "tool_execution",

            "workflow_state": {
                "step": random.randint(1,5),
                "completed": False
            },

            "status": random.choice([
                "running",
                "completed",
                "paused"
            ])

        }).execute()

        workflow_ids.append(workflow.data[0]["workflow_id"])

    print(f"✅ {len(workflow_ids)} Workflow Runs Created")


# --------------------------------------------------
# Seed Reminders
# --------------------------------------------------

def seed_reminders():

    print_header("Seeding Reminders")

    for _ in range(20):

        supabase.table("reminders").insert({

            "patient_id": random.choice(patient_ids),

            "appointment_id": random.choice(appointment_ids),

            "reminder_type": "Appointment Reminder",

            "reminder_time": random_datetime(15).isoformat(),

            "status": "pending"

        }).execute()

    print("✅ 20 Reminders Created")


# --------------------------------------------------
# Seed Escalations
# --------------------------------------------------

def seed_escalations():

    print_header("Seeding Escalations")

    reasons = [
        "Medicine Request",
        "Emergency Symptoms",
        "Doctor Approval Required",
        "Unsafe Query"
    ]

    for _ in range(5):

        supabase.table("escalations").insert({

            "workflow_id": random.choice(workflow_ids),

            "patient_id": random.choice(patient_ids),

            "reason": random.choice(reasons),

            "status": "pending",

            "assigned_to": random.choice(user_ids)

        }).execute()

    print("✅ 5 Escalations Created")


# --------------------------------------------------
# Seed Audit Events
# --------------------------------------------------

def seed_audit_events():

    print_header("Seeding Audit Events")

    tools = [
        "PatientTool",
        "AppointmentTool",
        "DocumentTool",
        "ReminderTool"
    ]

    for _ in range(30):

        supabase.table("audit_events").insert({

            "workflow_id": random.choice(workflow_ids),

            "agent_name": random.choice([
                "Supervisor",
                "Registration",
                "Appointment",
                "Document",
                "Safety"
            ]),

            "tool_name": random.choice(tools),

            "action": "Tool Executed",

            "status": "success",

            "metadata": {
                "execution_time_ms": random.randint(100,1500)
            }

        }).execute()

    print("✅ 30 Audit Events Created")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n🚀 Starting Database Seeding...\n")

    seed_users()
    seed_doctors()
    seed_patients()
    seed_appointment_slots()
    seed_appointments()
    seed_documents()
    seed_workflows()
    seed_reminders()
    seed_escalations()
    seed_audit_events()

    print("\n🎉 Database Seed Completed Successfully!")


if __name__ == "__main__":
    main()