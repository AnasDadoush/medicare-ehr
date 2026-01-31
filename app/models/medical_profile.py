from app import db

class MedicalProfile(db.Model):
    __tablename__ = 'medical_profiles'

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patients.id'),
        unique=True,
        nullable=False
    )

    blood_type = db.Column(db.String(3))
    height = db.Column(db.Integer)
    weight = db.Column(db.Float)

    chronic_diseases = db.Column(db.Text)
    allergies = db.Column(db.Text)
    general_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    medical_cases = db.relationship(
        'MedicalCase',
        backref='medical_profile',
        cascade='all, delete'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'blood_type': self.blood_type,
            'height': self.height,
            'weight': self.weight,
            'chronic_diseases': self.chronic_diseases,
            'allergies': self.allergies,
            'general_notes': self.general_notes
        }
