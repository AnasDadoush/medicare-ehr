from datetime import datetime
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    appointment_type = db.Column(db.String(100), default='عام')
    status = db.Column(db.String(50), default='مجدول')
    notes = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('User', backref=db.backref('appointments', lazy=True))
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_date} {self.appointment_time}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else '',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else '',
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d') if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'duration_minutes': self.duration_minutes,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }