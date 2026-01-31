from flask import request, redirect, url_for
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                
                if identity['role'] not in allowed_roles:
                    return redirect(url_for('auth.login'))
                
                return f(*args, **kwargs)
            except:
                return redirect(url_for('auth.login'))
        return decorated_function
    return decorator

# اختصارات للأدوار
def admin_required(f):
    return role_required(['ADMIN'])(f)

def doctor_required(f):
    return role_required(['ADMIN', 'DOCTOR'])(f)

def assistant_required(f):
    return role_required(['ADMIN', 'DOCTOR', 'ASSISTANT'])(f)