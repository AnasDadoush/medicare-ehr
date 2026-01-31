from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask import session
from datetime import datetime, timedelta, date
from app import db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from functools import wraps
import json

appointments_bp = Blueprint('appointments', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    return {
        'id': session.get('user_id'),
        'role': session.get('role'),
        'full_name': session.get('full_name'),
        'username': session.get('username')
    }

@appointments_bp.route('/appointments')
@login_required
def appointments_list():
    """قائمة المواعيد"""
    current_user = get_current_user()
    
    # جلب المواعيد حسب دور المستخدم
    if current_user['role'] == 'DOCTOR':
        appointments = Appointment.query.filter_by(doctor_id=current_user['id'])\
            .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())\
            .all()
    else:
        appointments = Appointment.query\
            .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())\
            .all()
    
    # جلب المرضى والأطباء للقوائم المنسدلة
    patients = Patient.query.order_by(Patient.first_name).all()
    doctors = User.query.filter_by(role='DOCTOR').order_by(User.full_name).all()
    
    return render_template('appointments/list.html',
                         appointments=appointments,
                         patients=patients,
                         doctors=doctors,
                         current_user=current_user)

@appointments_bp.route('/appointments/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    """إنشاء موعد جديد"""
    current_user = get_current_user()

    if request.method == 'POST':
        try:
            # جلب البيانات من النموذج
            patient_id = request.form.get('patient_id')
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            appointment_type = request.form.get('appointment_type', 'عام')
            duration = request.form.get('duration', 30)
            notes = request.form.get('notes', '')
            
            # استخدام الطبيب الحالي إذا كان الطبيب، أو اختيار طبيب من القائمة
            current_user_role = current_user['role']
            if current_user_role == 'DOCTOR':
                doctor_id = current_user['id']
            else:
                doctor_id = request.form.get('doctor_id')
            
            # إنشاء الموعد
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
                appointment_time=datetime.strptime(appointment_time, '%H:%M').time(),
                duration_minutes=duration,
                appointment_type=appointment_type,
                notes=notes,
                status='مجدول'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('تم إنشاء الموعد بنجاح', 'success')
            return redirect(url_for('appointments.appointments_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء الموعد: {str(e)}', 'danger')
    
    # جلب البيانات للقوائم المنسدلة
    patients = Patient.query.order_by(Patient.first_name).all()
    doctors = User.query.filter_by(role='DOCTOR').order_by(User.full_name).all()
    
    # التاريخ الحالي كتاريخ افتراضي
    today = date.today()
    next_week = today + timedelta(days=7)
    
    return render_template('appointments/create.html',
                         patients=patients,
                         doctors=doctors,
                         today=today.strftime('%Y-%m-%d'),
                         next_week=next_week.strftime('%Y-%m-%d'),
                         current_user=current_user)  # تم إضافة هذا

@appointments_bp.route('/appointments/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    """تعديل موعد"""
    current_user = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'POST':
        try:
            appointment.patient_id = request.form.get('patient_id')
            appointment.doctor_id = request.form.get('doctor_id')
            appointment.appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date()
            appointment.appointment_time = datetime.strptime(request.form.get('appointment_time'), '%H:%M').time()
            appointment.duration_minutes = request.form.get('duration', 30)
            appointment.appointment_type = request.form.get('appointment_type', 'عام')
            appointment.status = request.form.get('status', 'مجدول')
            appointment.notes = request.form.get('notes', '')
            
            db.session.commit()
            flash('تم تعديل الموعد بنجاح', 'success')
            return redirect(url_for('appointments.appointments_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تعديل الموعد: {str(e)}', 'danger')
    
    # جلب البيانات للقوائم المنسدلة
    patients = Patient.query.order_by(Patient.first_name).all()
    doctors = User.query.filter_by(role='DOCTOR').order_by(User.full_name).all()
    
    return render_template('appointments/edit.html',
                         appointment=appointment,
                         patients=patients,
                         doctors=doctors,
                         current_user=current_user,
                         now=datetime.now())  

@appointments_bp.route('/appointments/<int:appointment_id>/delete', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    """حذف موعد"""
    current_user = get_current_user()

    appointment = Appointment.query.get_or_404(appointment_id)
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('تم حذف الموعد بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الموعد: {str(e)}', 'danger')
    
    return redirect(url_for('appointments.appointments_list'))

@appointments_bp.route('/appointments/<int:appointment_id>/update-status', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    """تحديث حالة الموعد"""
    current_user = get_current_user()

    appointment = Appointment.query.get_or_404(appointment_id)
    status = request.form.get('status')
    
    if status in ['مجدول', 'تم الحضور', 'ملغي', 'لم يحضر']:
        appointment.status = status
        db.session.commit()
        flash(f'تم تحديث حالة الموعد إلى "{status}"', 'success')
    else:
        flash('حالة غير صالحة', 'danger')
    
    return redirect(url_for('appointments.appointments_list'))

@appointments_bp.route('/appointments/calendar')
@login_required
def appointments_calendar():
    """تقويم المواعيد"""
    current_user = get_current_user()

    
    # جلب المواعيد للأشهر الثلاثة القادمة
    today = date.today()
    three_months_later = today + timedelta(days=90)
    
    if current_user['role'] == 'DOCTOR':
        appointments = Appointment.query.filter(
            Appointment.doctor_id == current_user['id'],
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= three_months_later
        ).all()
    else:
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= three_months_later
        ).all()
    
    # تحويل المواعيد إلى تنسيق مناسب للتقويم
    calendar_events = []
    for appt in appointments:
        start_datetime = datetime.combine(appt.appointment_date, appt.appointment_time)
        end_datetime = start_datetime + timedelta(minutes=appt.duration_minutes)
        
        # تحديد لون حسب حالة الموعد
        color_map = {
            'مجدول': '#0d6efd',
            'تم الحضور': '#198754',
            'ملغي': '#dc3545',
            'لم يحضر': '#ffc107'
        }
        
        calendar_events.append({
            'id': appt.id,
            'title': f'{appt.patient.first_name} {appt.patient.last_name} - {appt.appointment_type}',
            'start': start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'color': color_map.get(appt.status, '#0d6efd'),
            'patient': f'{appt.patient.first_name} {appt.patient.last_name}',
            'doctor': appt.doctor.full_name,
            'type': appt.appointment_type,
            'status': appt.status,
            'notes': appt.notes
        })
    
    return render_template('appointments/calendar.html',
                         calendar_events=json.dumps(calendar_events),
                         current_user=current_user)

@appointments_bp.route('/api/appointments', methods=['GET'])
@login_required
def get_appointments_api():
    """API لجلب المواعيد"""
    current_user = get_current_user()

    
    # المعلمات
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    # بناء الاستعلام
    query = Appointment.query
    
    if current_user['role'] == 'DOCTOR':
        query = query.filter_by(doctor_id=current_user['id'])
    
    if start_date and end_date:
        query = query.filter(
            Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
    
    appointments = query.all()
    
    # تحويل إلى تنسيق JSON
    appointments_data = []
    for appt in appointments:
        appointments_data.append(appt.to_dict())
    
    return jsonify(appointments_data)

@appointments_bp.route('/api/appointments/upcoming')
@login_required
def upcoming_appointments():
    """المواعيد القادمة"""
    current_user = get_current_user()

    
    today = date.today()
    
    if current_user['role'] == 'DOCTOR':
        upcoming = Appointment.query.filter(
            Appointment.doctor_id == current_user['id'],
            Appointment.appointment_date >= today,
            Appointment.status == 'مجدول'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time)\
         .limit(10).all()
    else:
        upcoming = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'مجدول'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time)\
         .limit(10).all()
    
    return jsonify([appt.to_dict() for appt in upcoming])