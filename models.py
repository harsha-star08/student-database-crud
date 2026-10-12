from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class Student(BaseModel):
    name: str
    date_of_birth: date
    email: EmailStr
    phone: Optional[str] = None
    course: Optional[str] = None

    