from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # ADMIN | DOCTOR | ASSISTANT
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """تحويل إلى قاموس (لا نرسل كلمة المرور)"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_session_data(self):
        """الحصول على بيانات الجلسة"""
        return {
            'user_id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name
        }