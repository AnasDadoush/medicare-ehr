from app import db

# Re-export model classes so existing imports like `from app.models import User` continue to work
from .user import User
from .patient import Patient
from .medical_profile import MedicalProfile
from .medical_case import MedicalCase

__all__ = [
    'db',
    'User',
    'Patient',
    'MedicalProfile',
    'MedicalCase',
]
