from pydantic import BaseModel, EmailStr
from typing import Optional


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    age: int
    blood_group: Optional[str] = None
    phone: str
    email: EmailStr
    address: str