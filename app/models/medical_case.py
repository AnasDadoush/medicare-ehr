from app import db

class MedicalCase(db.Model):
    __tablename__ = 'medical_cases'

    id = db.Column(db.Integer, primary_key=True)

    medical_profile_id = db.Column(
        db.Integer,
        db.ForeignKey('medical_profiles.id'),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    case_date = db.Column(db.Date, nullable=False)

    case_description = db.Column(db.Text)
    treatment_details = db.Column(db.Text)
    prescribed_medications = db.Column(db.Text)
    lab_tests_and_results = db.Column(db.Text)
    visited_facilities = db.Column(db.Text)
    additional_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'medical_profile_id': self.medical_profile_id,
            'doctor_id': self.doctor_id,
            'case_date': self.case_date.isoformat(),
            'case_description': self.case_description,
            'treatment_details': self.treatment_details,
            'prescribed_medications': self.prescribed_medications,
            'lab_tests_and_results': self.lab_tests_and_results,
            'visited_facilities': self.visited_facilities,
            'additional_notes': self.additional_notes
        }
