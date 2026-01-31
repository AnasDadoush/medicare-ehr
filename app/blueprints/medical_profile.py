from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
from app import db
from app.models.medical_profile import MedicalProfile
from app.models.patient import Patient
from app.models.user import User
from datetime import datetime

medical_profiles_bp = Blueprint('medical_profiles', __name__)

# ============== Middleware Functions باستخدام الجلسات ==============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
        return f(*args, **kwargs)
    return decorated_function

def doctor_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
        
        if session.get('role') not in ['ADMIN', 'DOCTOR']:
            return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
        
        if session.get('role') not in ['ADMIN', 'DOCTOR', 'ASSISTANT']:
            return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============== HTML Routes ==============
@medical_profiles_bp.route('/medical-profiles/<int:patient_id>/update', methods=['GET'])
def update_medical_profile_page(patient_id):
    """صفحة تحديث الملف الطبي"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return render_template('auth/login.html', error='صلاحيات غير كافية')
    
    patient = Patient.query.get_or_404(patient_id)
    medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
    
    if not medical_profile:
        # إنشاء ملف طبي جديد إذا لم يكن موجوداً
        medical_profile = MedicalProfile(patient_id=patient_id)
        db.session.add(medical_profile)
        db.session.commit()
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('medical_profiles/update.html',
                         patient=patient,
                         medical_profile=medical_profile,
                         current_user=current_user)

# ============== API Routes (CRUD Operations) ==============
@medical_profiles_bp.route('/api/medical-profiles/patient/<int:patient_id>', methods=['GET'])
def get_medical_profile_by_patient(patient_id):
    """API: الحصول على الملف الطبي لمريض"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR', 'ASSISTANT']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        patient = Patient.query.get_or_404(patient_id)
        medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
        
        if not medical_profile:
            # إنشاء ملف طبي تلقائي إذا لم يكن موجوداً
            medical_profile = MedicalProfile(patient_id=patient_id)
            db.session.add(medical_profile)
            db.session.commit()
        
        # حساب مؤشر كتلة الجسم (BMI) إذا كان الطول والوزن موجودين
        bmi = None
        if medical_profile.height and medical_profile.weight:
            height_in_meters = medical_profile.height / 100
            bmi = round(medical_profile.weight / (height_in_meters ** 2), 2)
        
        profile_data = medical_profile.to_dict()
        profile_data['bmi'] = bmi
        profile_data['bmi_status'] = get_bmi_status(bmi) if bmi else None
        profile_data['patient'] = patient.to_dict()
        
        return jsonify({
            'success': True,
            'medical_profile': profile_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_profiles_bp.route('/api/medical-profiles/<int:profile_id>', methods=['GET'])
def get_medical_profile(profile_id):
    """API: الحصول على ملف طبي"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_profile = MedicalProfile.query.get_or_404(profile_id)
        
        # حساب BMI
        bmi = None
        if medical_profile.height and medical_profile.weight:
            height_in_meters = medical_profile.height / 100
            bmi = round(medical_profile.weight / (height_in_meters ** 2), 2)
        
        profile_data = medical_profile.to_dict()
        profile_data['bmi'] = bmi
        profile_data['bmi_status'] = get_bmi_status(bmi) if bmi else None
        profile_data['patient'] = medical_profile.patient.to_dict() if medical_profile.patient else None
        
        return jsonify({
            'success': True,
            'medical_profile': profile_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_profiles_bp.route('/api/medical-profiles/<int:profile_id>', methods=['PUT'])
def update_medical_profile_api(profile_id):
    """API: تحديث ملف طبي"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_profile = MedicalProfile.query.get_or_404(profile_id)
        data = request.get_json()
        
        # تحديث الحقول المسموح بها
        allowed_fields = [
            'blood_type', 'height', 'weight',
            'chronic_diseases', 'allergies', 'general_notes'
        ]
        
        updates_made = False
        for field in allowed_fields:
            if field in data and getattr(medical_profile, field) != data[field]:
                setattr(medical_profile, field, data[field])
                updates_made = True
        
        if updates_made:
            db.session.commit()
            
            # حساب BMI بعد التحديث
            bmi = None
            if medical_profile.height and medical_profile.weight:
                height_in_meters = medical_profile.height / 100
                bmi = round(medical_profile.weight / (height_in_meters ** 2), 2)
            
            profile_data = medical_profile.to_dict()
            profile_data['bmi'] = bmi
            profile_data['bmi_status'] = get_bmi_status(bmi) if bmi else None
            
            return jsonify({
                'success': True,
                'message': 'تم تحديث الملف الطبي بنجاح',
                'medical_profile': profile_data
            })
        else:
            return jsonify({
                'success': True,
                'message': 'لم يتم إجراء أي تغييرات',
                'medical_profile': medical_profile.to_dict()
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_profiles_bp.route('/api/medical-profiles/patient/<int:patient_id>', methods=['PUT'])
def update_medical_profile_by_patient_api(patient_id):
    """API: تحديث الملف الطبي باستخدام معرف المريض"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
        
        if not medical_profile:
            # إنشاء ملف طبي جديد
            medical_profile = MedicalProfile(patient_id=patient_id)
            db.session.add(medical_profile)
        
        data = request.get_json()
        
        # تحديث الحقول
        allowed_fields = [
            'blood_type', 'height', 'weight',
            'chronic_diseases', 'allergies', 'general_notes'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(medical_profile, field, data[field])
        
        db.session.commit()
        
        # حساب BMI
        bmi = None
        if medical_profile.height and medical_profile.weight:
            height_in_meters = medical_profile.height / 100
            bmi = round(medical_profile.weight / (height_in_meters ** 2), 2)
        
        profile_data = medical_profile.to_dict()
        profile_data['bmi'] = bmi
        profile_data['bmi_status'] = get_bmi_status(bmi) if bmi else None
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث الملف الطبي بنجاح',
            'medical_profile': profile_data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500
# ============== Helper Functions ==============
def get_bmi_status(bmi):
    """تحديد حالة مؤشر كتلة الجسم"""
    if bmi is None:
        return 'غير محسوب'
    elif bmi < 18.5:
        return 'نحيف'
    elif 18.5 <= bmi <= 24.9:
        return 'طبيعي'
    elif 25 <= bmi <= 29.9:
        return 'وزن زائد'
    elif 30 <= bmi <= 34.9:
        return 'سمنة درجة أولى'
    elif 35 <= bmi <= 39.9:
        return 'سمنة درجة ثانية'
    else:
        return 'سمنة مفرطة'