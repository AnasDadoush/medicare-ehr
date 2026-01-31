from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps
from app import db
from app.models.patient import Patient
from app.models.medical_case import MedicalCase
from app.models.user import User
from app.models.medical_profile import MedicalProfile
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    # إحصائيات المرضى
    total_patients = Patient.query.count()
    
    # المرضى الجدد هذا الشهر
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_patients_this_month = Patient.query.filter(
        Patient.created_at >= first_day_of_month
    ).count()
    
    # إحصائيات الحالات المرضية (للأطباء والمديرين فقط)
    total_medical_cases = 0
    today_cases = 0
    if current_user['role'] in ['ADMIN', 'DOCTOR']:
        total_medical_cases = MedicalCase.query.count()
        
        # الحالات المرضية اليوم
        today = datetime.now().date()
        today_cases = MedicalCase.query.filter(
            func.date(MedicalCase.case_date) == today
        ).count()
    
    # المرضى حسب الجنس
    male_patients = Patient.query.filter_by(gender='ذكر').count()
    female_patients = Patient.query.filter_by(gender='أنثى').count()
    other_patients = total_patients - male_patients - female_patients
    
    # المرضى الذين لديهم ملفات طبية
    patients_with_profiles = db.session.query(Patient).join(MedicalProfile).count()
    
    # أكثر الأمراض المزمنة شيوعاً
    from collections import Counter
    import re
    
    common_diseases = []
    profiles = MedicalProfile.query.filter(
        MedicalProfile.chronic_diseases.isnot(None),
        MedicalProfile.chronic_diseases != ''
    ).all()
    
    if profiles:
        diseases_text = ' '.join([p.chronic_diseases.lower() for p in profiles])
        disease_keywords = ['سكري', 'ضغط', 'ربو', 'قلب', 'كولسترول', 'حساسية']
        
        disease_counts = {}
        for keyword in disease_keywords:
            count = len(re.findall(keyword, diseases_text))
            if count > 0:
                disease_counts[keyword] = count
        
        common_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # أحدث المرضى المسجلين
    recent_patients = Patient.query.order_by(
        Patient.created_at.desc()
    ).limit(5).all()
    
    # إعداد الإحصائيات
    stats = {
        'patients': total_patients,
        'new_patients_month': new_patients_this_month,
        'medical_cases': total_medical_cases,
        'today_cases': today_cases,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'other_patients': other_patients,
        'patients_with_profiles': patients_with_profiles,
        'patients_without_profiles': total_patients - patients_with_profiles
    }
    
    # البيانات للرسم البياني
    # المرضى المسجلين في آخر 6 أشهر
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_patients_data = []
    for i in range(6):
        month = datetime.now() - timedelta(days=30*i)
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        count = Patient.query.filter(
            Patient.created_at >= month_start,
            Patient.created_at < next_month
        ).count()
        
        monthly_patients_data.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
    
    monthly_patients_data.reverse()
    
    return render_template('dashboard/index.html',
                         current_user=current_user,
                         stats=stats,
                         recent_patients=recent_patients,
                         common_diseases=common_diseases,
                         monthly_patients_data=monthly_patients_data,
                         now=datetime.now())  
