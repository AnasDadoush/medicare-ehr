from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
from app import db
from app.models.medical_case import MedicalCase
from app.models.medical_profile import MedicalProfile
from app.models.patient import Patient
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import or_, func, extract
import json

medical_cases_bp = Blueprint('medical_cases', __name__)

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

# ============== HTML Routes ==============
@medical_cases_bp.route('/medical-cases')
def medical_cases_page():
    """صفحة قائمة الحالات المرضية"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return render_template('auth/login.html', error='صلاحيات غير كافية')
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('medical_cases/list.html', current_user=current_user)

@medical_cases_bp.route('/medical-cases/create', methods=['GET'])
def create_medical_case_page():
    """صفحة إنشاء حالة مرضية جديدة"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return render_template('auth/login.html', error='صلاحيات غير كافية')
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    # الحصول على قائمة المرضى
    patients = Patient.query.all()
    patients_list = [{'id': p.id, 'name': p.full_name()} for p in patients]
    
    # الحصول على قائمة الأطباء
    doctors = User.query.filter_by(role='DOCTOR', is_active=True).all()
    doctors_list = [{'id': d.id, 'name': d.full_name} for d in doctors]
    
    return render_template('medical_cases/create.html',
                         current_user=current_user,
                         patients=patients_list,
                         doctors=doctors_list)

@medical_cases_bp.route('/medical-cases/<int:case_id>', methods=['GET'])
def view_medical_case_page(case_id):
    """صفحة معاينة حالة مرضية"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return render_template('auth/login.html', error='صلاحيات غير كافية')
    
    medical_case = MedicalCase.query.get_or_404(case_id)
    
    # التحقق من الصلاحيات
    current_user_id = session.get('user_id')
    if session.get('role') == 'DOCTOR' and medical_case.doctor_id != current_user_id:
        return redirect(url_for('medical_cases.medical_cases_page'))
    
    # الحصول على بيانات إضافية
    medical_profile = MedicalProfile.query.get(medical_case.medical_profile_id)
    patient = Patient.query.get(medical_profile.patient_id) if medical_profile else None
    doctor = User.query.get(medical_case.doctor_id)
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('medical_cases/view.html',
                         medical_case=medical_case,
                         patient=patient,
                         doctor=doctor,
                         medical_profile=medical_profile,
                         current_user=current_user)

@medical_cases_bp.route('/medical-cases/<int:case_id>/edit', methods=['GET'])
def edit_medical_case_page(case_id):
    """صفحة تعديل حالة مرضية"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return render_template('auth/login.html', error='صلاحيات غير كافية')
    
    medical_case = MedicalCase.query.get_or_404(case_id)
    
    # التحقق من الصلاحيات
    current_user_id = session.get('user_id')
    if session.get('role') == 'DOCTOR' and medical_case.doctor_id != current_user_id:
        return redirect(url_for('medical_cases.medical_cases_page'))
    
    # الحصول على بيانات إضافية
    medical_profile = MedicalProfile.query.get(medical_case.medical_profile_id)
    patient = Patient.query.get(medical_profile.patient_id) if medical_profile else None
    
    # الحصول على قائمة الأطباء (للإدارة فقط)
    doctors = []
    if session.get('role') == 'ADMIN':
        doctors = User.query.filter_by(role='DOCTOR', is_active=True).all()
    
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('medical_cases/edit.html',
                         medical_case=medical_case,
                         patient=patient,
                         doctors=doctors,
                         current_user=current_user)

# ============== API Routes (CRUD Operations) ==============
@medical_cases_bp.route('/api/medical-cases', methods=['GET'])
def list_medical_cases_api():
    """API: الحصول على قائمة الحالات المرضية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        # معلمات البحث
        search = request.args.get('search', '')
        patient_id = request.args.get('patient_id', '')
        doctor_id = request.args.get('doctor_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        sort_by = request.args.get('sort_by', 'case_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # بناء الاستعلام
        query = MedicalCase.query
        
        # فلترة حسب المريض
        if patient_id and patient_id.isdigit():
            medical_profile = MedicalProfile.query.filter_by(patient_id=int(patient_id)).first()
            if medical_profile:
                query = query.filter_by(medical_profile_id=medical_profile.id)
        
        # فلترة حسب الطبيب
        if doctor_id and doctor_id.isdigit():
            query = query.filter_by(doctor_id=int(doctor_id))
        
        # فلترة حسب الطبيب الحالي (إذا كان طبيباً)
        if session.get('role') == 'DOCTOR':
            query = query.filter_by(doctor_id=session.get('user_id'))
        
        # فلترة حسب التاريخ
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(MedicalCase.case_date >= start_date_obj)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(MedicalCase.case_date <= end_date_obj)
            except ValueError:
                pass
        
        # البحث النصي
        if search:
            search_filter = or_(
                MedicalCase.case_description.ilike(f'%{search}%'),
                MedicalCase.treatment_details.ilike(f'%{search}%'),
                MedicalCase.prescribed_medications.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # تطبيق الترتيب
        if hasattr(MedicalCase, sort_by):
            column = getattr(MedicalCase, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(MedicalCase.case_date.desc())
        
        # التقطيع للصفحات
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # إعداد البيانات للإرجاع
        cases_data = []
        for case in pagination.items:
            case_dict = case.to_dict()
            
            # إضافة معلومات إضافية
            medical_profile = MedicalProfile.query.get(case.medical_profile_id)
            if medical_profile:
                patient = Patient.query.get(medical_profile.patient_id)
                case_dict['patient_name'] = patient.full_name() if patient else 'غير معروف'
                case_dict['patient_id'] = patient.id if patient else None
            
            doctor = User.query.get(case.doctor_id)
            case_dict['doctor_name'] = doctor.full_name if doctor else 'غير معروف'
            
            cases_data.append(case_dict)
        
        return jsonify({
            'success': True,
            'medical_cases': cases_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_cases_bp.route('/api/medical-cases', methods=['POST'])
def create_medical_case_api():
    """API: إنشاء حالة مرضية جديدة"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['medical_profile_id', 'case_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
        
        # استخدام الطبيب الحالي إذا لم يتم تحديد طبيب
        doctor_id = data.get('doctor_id', session.get('user_id'))
        
        # تحقق إذا كان الطبيب المحدد موجوداً ونشطاً
        doctor = User.query.get(doctor_id)
        if not doctor or doctor.role != 'DOCTOR' or not doctor.is_active:
            return jsonify({'success': False, 'message': 'الطبيب غير موجود أو غير نشط'}), 400
        
        # إنشاء الحالة المرضية
        medical_case = MedicalCase(
            medical_profile_id=data['medical_profile_id'],
            doctor_id=doctor_id,
            case_date=datetime.strptime(data['case_date'], '%Y-%m-%d').date(),
            case_description=data.get('case_description', ''),
            treatment_details=data.get('treatment_details', ''),
            prescribed_medications=data.get('prescribed_medications', ''),
            lab_tests_and_results=data.get('lab_tests_and_results', ''),
            visited_facilities=data.get('visited_facilities', ''),
            additional_notes=data.get('additional_notes', '')
        )
        
        db.session.add(medical_case)
        db.session.commit()
        
        # الحصول على بيانات المريض لإرجاعها
        medical_profile = MedicalProfile.query.get(medical_case.medical_profile_id)
        patient = Patient.query.get(medical_profile.patient_id) if medical_profile else None
        
        case_data = medical_case.to_dict()
        case_data['patient_name'] = patient.full_name() if patient else 'غير معروف'
        case_data['doctor_name'] = doctor.full_name
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الحالة المرضية بنجاح',
            'medical_case': case_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_cases_bp.route('/api/medical-cases/<int:case_id>', methods=['GET'])
def get_medical_case_api(case_id):
    """API: الحصول على حالة مرضية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_case = MedicalCase.query.get_or_404(case_id)
        
        # التحقق من الصلاحيات
        current_user_id = session.get('user_id')
        if session.get('role') == 'DOCTOR' and medical_case.doctor_id != current_user_id:
            return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
        
        # الحصول على بيانات إضافية
        medical_profile = MedicalProfile.query.get(medical_case.medical_profile_id)
        patient = Patient.query.get(medical_profile.patient_id) if medical_profile else None
        doctor = User.query.get(medical_case.doctor_id)
        
        case_data = medical_case.to_dict()
        case_data['patient'] = patient.to_dict() if patient else None
        case_data['doctor'] = doctor.to_dict() if doctor else None
        case_data['medical_profile'] = medical_profile.to_dict() if medical_profile else None
        
        return jsonify({
            'success': True,
            'medical_case': case_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_cases_bp.route('/api/medical-cases/<int:case_id>', methods=['PUT'])
def update_medical_case_api(case_id):
    """API: تحديث حالة مرضية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_case = MedicalCase.query.get_or_404(case_id)
        
        # التحقق من الصلاحيات
        current_user_id = session.get('user_id')
        if session.get('role') == 'DOCTOR' and medical_case.doctor_id != current_user_id:
            return jsonify({'success': False, 'message': 'لا يمكنك تعديل هذه الحالة'}), 403
        
        data = request.get_json()
        
        # تحديث الحقول المسموح بها
        allowed_fields = [
            'case_date', 'case_description', 'treatment_details',
            'prescribed_medications', 'lab_tests_and_results',
            'visited_facilities', 'additional_notes'
        ]
        
        updates_made = False
        for field in allowed_fields:
            if field in data and getattr(medical_case, field) != data[field]:
                if field == 'case_date':
                    setattr(medical_case, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(medical_case, field, data[field])
                updates_made = True
        
        # فقط المدير يمكنه تغيير الطبيب
        if session.get('role') == 'ADMIN' and 'doctor_id' in data:
            doctor = User.query.get(data['doctor_id'])
            if doctor and doctor.role == 'DOCTOR' and doctor.is_active:
                medical_case.doctor_id = data['doctor_id']
                updates_made = True
        
        if updates_made:
            db.session.commit()
            
            # الحصول على البيانات المحدثة
            medical_profile = MedicalProfile.query.get(medical_case.medical_profile_id)
            patient = Patient.query.get(medical_profile.patient_id) if medical_profile else None
            doctor = User.query.get(medical_case.doctor_id)
            
            case_data = medical_case.to_dict()
            case_data['patient_name'] = patient.full_name() if patient else 'غير معروف'
            case_data['doctor_name'] = doctor.full_name if doctor else 'غير معروف'
            
            return jsonify({
                'success': True,
                'message': 'تم تحديث الحالة المرضية بنجاح',
                'medical_case': case_data
            })
        else:
            return jsonify({
                'success': True,
                'message': 'لم يتم إجراء أي تغييرات',
                'medical_case': medical_case.to_dict()
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_cases_bp.route('/api/medical-cases/<int:case_id>', methods=['DELETE'])
def delete_medical_case_api(case_id):
    """API: حذف حالة مرضية"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_case = MedicalCase.query.get_or_404(case_id)
        
        # التحقق من الصلاحيات
        current_user_id = session.get('user_id')
        if session.get('role') == 'DOCTOR' and medical_case.doctor_id != current_user_id:
            return jsonify({'success': False, 'message': 'لا يمكنك حذف هذه الحالة'}), 403
        
        db.session.delete(medical_case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف الحالة المرضية بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@medical_cases_bp.route('/api/medical-cases/patient/<int:patient_id>', methods=['GET'])
def get_patient_medical_cases_api(patient_id):
    """API: الحصول على الحالات المرضية لمريض"""
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    # التحقق من الصلاحيات
    if session.get('role') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'success': False, 'message': 'صلاحيات غير كافية'}), 403
    
    try:
        medical_profile = MedicalProfile.query.filter_by(patient_id=patient_id).first()
        
        if not medical_profile:
            return jsonify({
                'success': True,
                'medical_cases': [],
                'message': 'لا توجد حالات مرضية لهذا المريض'
            })
        
        cases = MedicalCase.query.filter_by(
            medical_profile_id=medical_profile.id
        ).order_by(MedicalCase.case_date.desc()).all()
        
        cases_data = []
        for case in cases:
            case_dict = case.to_dict()
            doctor = User.query.get(case.doctor_id)
            case_dict['doctor_name'] = doctor.full_name if doctor else 'غير معروف'
            cases_data.append(case_dict)
        
        return jsonify({
            'success': True,
            'medical_cases': cases_data,
            'total': len(cases_data),
            'patient_id': patient_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500