# seed_data.py
"""
إضافة بيانات تجريبية بعد إنشاء الجداول
تشغيل: python seed_data.py
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

print("="*60)
print("🌱 Adding Sample Data")
print("="*60)

# إضافة المسار
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_profile import MedicalProfile
from app.models.medical_case import MedicalCase
from app.models.appointment import Appointment

app = create_app()

with app.app_context():
    try:
        # ============== 1. إضافة المستخدمين ==============
        print("\n👤 Step 1: Adding users...")
        
        users_to_add = [
            {
                'full_name': 'مدير النظام',
                'username': 'admin',
                'password': 'admin123',
                'role': 'ADMIN'
            },
            {
                'full_name': 'د. أحمد محمد',
                'username': 'doctor1',
                'password': 'doctor123',
                'role': 'DOCTOR'
            },
            {
                'full_name': 'د. سارة عبدالله',
                'username': 'doctor2', 
                'password': 'doctor123',
                'role': 'DOCTOR'
            },
            {
                'full_name': 'مساعد العيادة',
                'username': 'assistant1',
                'password': 'assistant123',
                'role': 'ASSISTANT'
            }
        ]
        
        users_added = 0
        for user_data in users_to_add:
            # التحقق إذا كان المستخدم موجوداً
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    full_name=user_data['full_name'],
                    username=user_data['username'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                users_added += 1
                print(f"   ✅ Created: {user_data['username']} ({user_data['role']})")
            else:
                print(f"   ⏭️  Skipped: {user_data['username']} (already exists)")
        
        if users_added > 0:
            db.session.commit()
            print(f"✅ Added {users_added} new users")
        else:
            print("✅ All users already exist")
        
        # ============== 2. إضافة المرضى ==============
        print("\n👨‍⚕️ Step 2: Adding patients...")
        
        patients_to_add = [
            {
                'first_name': 'محمد',
                'last_name': 'علي',
                'gender': 'ذكر',
                'phone_number': '0551234567',
                'birth_date': datetime(1985, 5, 15).date()
            },
            {
                'first_name': 'فاطمة',
                'last_name': 'خالد',
                'gender': 'أنثى',
                'phone_number': '0549876543',
                'birth_date': datetime(1990, 8, 22).date()
            },
            {
                'first_name': 'عبدالله',
                'middle_name': 'سالم',
                'last_name': 'الزيد',
                'gender': 'ذكر',
                'phone_number': '0501122334',
                'birth_date': datetime(1978, 12, 3).date()
            }
        ]
        
        patients_added = 0
        for patient_data in patients_to_add:
            # التحقق إذا كان المريض موجوداً
            existing = Patient.query.filter_by(
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name']
            ).first()
            
            if not existing:
                patient = Patient(
                    first_name=patient_data['first_name'],
                    middle_name=patient_data.get('middle_name', ''),
                    last_name=patient_data['last_name'],
                    gender=patient_data['gender'],
                    phone_number=patient_data['phone_number'],
                    birth_date=patient_data.get('birth_date')
                )
                db.session.add(patient)
                patients_added += 1
                print(f"   ✅ Created: {patient.full_name()}")
            else:
                print(f"   ⏭️  Skipped: {patient_data['first_name']} {patient_data['last_name']} (already exists)")
        
        if patients_added > 0:
            db.session.commit()
            print(f"✅ Added {patients_added} new patients")
        else:
            print("✅ All patients already exist")
        
        # ============== 3. إضافة الملفات الطبية ==============
        print("\n📁 Step 3: Adding medical profiles...")
        
        # الحصول على جميع المرضى
        all_patients = Patient.query.all()
        
        profiles_added = 0
        for i, patient in enumerate(all_patients[:3]):  # أول 3 مرضى فقط
            existing_profile = MedicalProfile.query.filter_by(patient_id=patient.id).first()
            
            if not existing_profile:
                # بيانات تجريبية للملفات الطبية
                profile_data = {
                    'blood_type': ['O+', 'A+', 'B+'][i % 3],
                    'height': [175, 162, 180][i % 3],
                    'weight': [72.5, 58.0, 85.0][i % 3],
                    'chronic_diseases': ['سكري النوع الثاني', 'ضغط الدم', 'كولسترول'][i % 3],
                    'allergies': ['حساسية من البنسلين', 'لا توجد', 'حساسية من الغبار'][i % 3],
                    'general_notes': ['مريض منتظم على أدوية السكري', 
                                    'تأخذ دواء الضغط يومياً', 
                                    'يحتاج متابعة الكولسترول'][i % 3]
                }
                
                profile = MedicalProfile(
                    patient_id=patient.id,
                    **profile_data
                )
                db.session.add(profile)
                profiles_added += 1
                print(f"   ✅ Created profile for: {patient.full_name()}")
            else:
                print(f"   ⏭️  Skipped profile for: {patient.full_name()} (already exists)")
        
        if profiles_added > 0:
            db.session.commit()
            print(f"✅ Added {profiles_added} new medical profiles")
        else:
            print("✅ All medical profiles already exist")
        
        # ============== 4. عرض ملخص ==============
        print("\n" + "="*60)
        print("📊 DATABASE SUMMARY")
        print("="*60)
        
        print(f"👥 Users: {User.query.count()}")
        print(f"👨‍⚕️ Patients: {Patient.query.count()}")
        print(f"📁 Medical Profiles: {MedicalProfile.query.count()}")
        print(f"🏥 Medical Cases: {MedicalCase.query.count()}")
        print(f"📅 Appointments: {Appointment.query.count()}")
        
        print("\n🔑 Available Login Credentials:")
        users = User.query.all()
        for user in users:
            if user.role == 'ADMIN':
                print(f"   • {user.username} / admin123 (Admin)")
            elif user.role == 'DOCTOR':
                print(f"   • {user.username} / doctor123 (Doctor)")
            elif user.role == 'ASSISTANT':
                print(f"   • {user.username} / assistant123 (Assistant)")
        
        print("\n" + "="*60)
        print("✅ Data seeding completed!")
        print("="*60)
        
        print("\n🚀 Next: Run the application:")
        print("   python run.py")
        print("\n🌐 Then open: http://localhost:5000")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()