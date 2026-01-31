from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
from app import db
from app.models.patient import Patient
from app.models.medical_profile import MedicalProfile
from app.models.medical_case import MedicalCase
from app.models.user import User
from sqlalchemy import or_
from datetime import datetime
 
patients_bp = Blueprint('patients', __name__)

# ============== Middleware Functions ==============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        if session.get('role') not in ['ADMIN', 'DOCTOR', 'ASSISTANT']:
            return render_template('auth/login.html', error='صلاحيات غير كافية')
        
        return f(*args, **kwargs)
    return decorated_function

def doctor_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        if session.get('role') not in ['ADMIN', 'DOCTOR']:
            return render_template('auth/login.html', error='صلاحيات غير كافية')
        
        return f(*args, **kwargs)
    return decorated_function

# ============== HTML Routes ==============
@patients_bp.route('/patients')
@login_required
@staff_required
def patients_page():
    """صفحة قائمة المرضى"""
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('patients/list.html', current_user=current_user)

@patients_bp.route('/patients/create', methods=['GET'])
@login_required
@staff_required
def create_patient_page():
    """صفحة إنشاء مريض جديد"""
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('patients/create.html', current_user=current_user)

@patients_bp.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
@staff_required
def view_patient_page(patient_id):
    """صفحة معاينة المريض"""
    patient = Patient.query.get_or_404(patient_id)
    medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
    
    # الحصول على الحالات المرضية إذا كان المستخدم طبيب أو مدير
    medical_cases = []
    if session.get('role') in ['ADMIN', 'DOCTOR']:
        if medical_profile:
            medical_cases = MedicalCase.query.filter_by(
                medical_profile_id=medical_profile.id
            ).order_by(MedicalCase.case_date.desc()).all()
    
    # الحصول على بيانات الأطباء
    doctors = User.query.filter_by(role='DOCTOR', is_active=True).all() if session.get('role') in ['ADMIN', 'DOCTOR'] else []
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('patients/view.html',
                         patient=patient,
                         medical_profile=medical_profile,
                         medical_cases=medical_cases,
                         doctors=doctors,
                         current_user=current_user)

@patients_bp.route('/patients/<int:patient_id>/edit', methods=['GET'])
@login_required
@staff_required
def edit_patient_page(patient_id):
    """صفحة تعديل بيانات المريض"""
    patient = Patient.query.get_or_404(patient_id)
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('patients/edit.html', patient=patient, current_user=current_user)

# ============== API Routes (CRUD Operations) ==============
@patients_bp.route('/api/patients', methods=['GET'])
@login_required
@staff_required
def list_patients_api():
    """API: الحصول على قائمة المرضى مع البحث والفلترة"""
    try:
        # معلمات البحث
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # بناء الاستعلام
        query = Patient.query
        
        # تطبيق البحث
        if search:
            search_filter = or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.middle_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.phone_number.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # تطبيق الترتيب
        if hasattr(Patient, sort_by):
            column = getattr(Patient, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(Patient.created_at.desc())
        
        # التقطيع للصفحات
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # إعداد البيانات للإرجاع
        patients_data = []
        for patient in pagination.items:
            patient_dict = patient.to_dict()
            
            # إضافة معلومات إضافية
            medical_profile = MedicalProfile.query.filter_by(patient_id=patient.id).first()
            patient_dict['has_medical_profile'] = bool(medical_profile)
            patient_dict['medical_cases_count'] = MedicalCase.query.filter_by(
                medical_profile_id=medical_profile.id
            ).count() if medical_profile else 0
            
            patients_data.append(patient_dict)
        
        return jsonify({
            'success': True,
            'patients': patients_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients', methods=['POST'])
@login_required
@staff_required
def create_patient_api():
    """API: إنشاء مريض جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({'success': False, 'message': 'الاسم الأول والأخير مطلوبان'}), 400
        
        # إنشاء المريض
        patient = Patient(
            first_name=data['first_name'],
            middle_name=data.get('middle_name', ''),
            last_name=data['last_name'],
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            phone_number=data.get('phone_number', '')
        )
        
        db.session.add(patient)
        db.session.flush()  # للحصول على ID المريض
        
        # إنشاء ملف طبي تلقائي للمريض
        medical_profile = MedicalProfile(patient_id=patient.id)
        db.session.add(medical_profile)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء المريض بنجاح',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients/<int:patient_id>', methods=['GET'])
@login_required
@staff_required
def get_patient_api(patient_id):
    """API: الحصول على بيانات مريض"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # الحصول على الملف الطبي
        medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
        
        # عدد الحالات المرضية
        medical_cases_count = 0
        if medical_profile:
            medical_cases_count = MedicalCase.query.filter_by(
                medical_profile_id=medical_profile.id
            ).count()
        
        patient_data = patient.to_dict()
        patient_data['medical_profile'] = medical_profile.to_dict() if medical_profile else None
        patient_data['medical_cases_count'] = medical_cases_count
        
        return jsonify({'success': True, 'patient': patient_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients/<int:patient_id>', methods=['PUT'])
@login_required
@staff_required
def update_patient_api(patient_id):
    """API: تحديث بيانات مريض"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # تحديث البيانات
        allowed_fields = ['first_name', 'middle_name', 'last_name', 'gender', 'birth_date', 'phone_number']
        for field in allowed_fields:
            if field in data:
                setattr(patient, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث بيانات المريض بنجاح',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@login_required
@staff_required
def delete_patient_api(patient_id):
    """API: حذف مريض"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # التحقق من وجود حالات مرضية قبل الحذف
        medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
        if medical_profile:
            cases_count = MedicalCase.query.filter_by(medical_profile_id=medical_profile.id).count()
            if cases_count > 0:
                return jsonify({
                    'success': False,
                    'message': f'لا يمكن حذف المريض لأنه لديه {cases_count} حالة مرضية'
                }), 400
        
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المريض بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients/statistics', methods=['GET'])
@login_required
def get_patients_statistics():
    """API: إحصائيات المرضى"""
    try:
        total_patients = Patient.query.count()
        
        # حسب الجنس
        male_count = Patient.query.filter_by(gender='ذكر').count()
        female_count = Patient.query.filter_by(gender='أنثى').count()
        unknown_gender = total_patients - male_count - female_count
        
        # هذا الشهر
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_patients = Patient.query.filter(
            Patient.created_at >= first_day_of_month
        ).count()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total': total_patients,
                'male': male_count,
                'female': female_count,
                'unknown_gender': unknown_gender,
                'monthly_new': monthly_patients
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@patients_bp.route('/api/patients/export', methods=['GET'])
@login_required
@doctor_or_admin_required
def export_patients_api():
    """API: تصدير بيانات المرضى"""
    try:
        patients = Patient.query.all()
        
        # تحويل البيانات إلى قائمة
        patients_list = []
        for patient in patients:
            patient_data = patient.to_dict()
            
            # إضافة معلومات إضافية
            medical_profile = MedicalProfile.query.filter_by(patient_id=patient.id).first()
            if medical_profile:
                patient_data['blood_type'] = medical_profile.blood_type
                patient_data['chronic_diseases'] = medical_profile.chronic_diseases
                patient_data['allergies'] = medical_profile.allergies
            
            patients_list.append(patient_data)
        
        return jsonify({
            'success': True,
            'patients': patients_list,
            'exported_at': datetime.now().isoformat(),
            'total_records': len(patients_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500