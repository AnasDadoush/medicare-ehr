from app import db

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)

    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone_number = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    medical_profile = db.relationship(
        'MedicalProfile',
        backref='patient',
        uselist=False,
        cascade='all, delete'
    )

    def full_name(self):
        return " ".join(filter(None, [
            self.first_name,
            self.middle_name,
            self.last_name
        ]))

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name(),
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'phone_number': self.phone_number
        }
