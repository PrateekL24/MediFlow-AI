from fastapi import APIRouter
from backend.models.patient import PatientCreate
from backend.core.database import supabase

router = APIRouter(
    prefix="/registration",
    tags=["Registration"]
)


@router.post("/patient")
def register_patient(patient: PatientCreate):

    response = (
        supabase.table("patients")
        .insert(patient.model_dump())
        .execute()
    )

    return {
        "message": "Patient Registered Successfully",
        "patient": response.data[0]
    }