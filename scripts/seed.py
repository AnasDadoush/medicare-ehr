import sys
import os

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_profile import MedicalProfile
from app.models.medical_case import MedicalCase
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("🔍 التحقق من اتصال قاعدة البيانات...")
        
        try:
            # اختبار اتصال قاعدة البيانات
            db.session.execute("SELECT 1")
            print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        except Exception as e:
            print(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
            return
        
        # التحقق من الجداول
        print("\n🔍 التحقق من وجود الجداول...")
        try:
            # استعلام بسيط من كل جدول
            db.session.execute("SELECT 1 FROM users LIMIT 1")
            print("✅ جدول users موجود")
            
            db.session.execute("SELECT 1 FROM patients LIMIT 1")
            print("✅ جدول patients موجود")
            
            db.session.execute("SELECT 1 FROM medical_profiles LIMIT 1")
            print("✅ جدول medical_profiles موجود")
            
            db.session.execute("SELECT 1 FROM medical_cases LIMIT 1")
            print("✅ جدول medical_cases موجود")
            
        except Exception as e:
            print(f"❌ بعض الجداول مفقودة: {e}")
            print("⚠️  تأكد من أنك أنشأت الجداول يدوياً")
            return
        
        print("\n🌱 بدء عملية البذور...")
        
        # 1. إضافة المستخدمين إذا لم يكونوا موجودين
        users_to_create = [
            {
                'full_name': 'مدير النظام',
                'username': 'admin',
                'password': 'admin123',
                'role': 'ADMIN'
            },
            {
                'full_name': 'دكتور أحمد محمد',
                'username': 'doctor1',
                'password': 'doctor123',
                'role': 'DOCTOR'
            },
            {
                'full_name': 'مساعد إكلينيكي',
                'username': 'assistant1',
                'password': 'assistant123',
                'role': 'ASSISTANT'
            }
        ]
        
        for user_data in users_to_create:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    full_name=user_data['full_name'],
                    username=user_data['username'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"✅ تم إنشاء مستخدم: {user_data['username']}")
            else:
                print(f"⚠️  المستخدم موجود بالفعل: {user_data['username']}")
        
        db.session.commit()
        
        # 2. إضافة مرضى إذا لم يكن هناك مرضى
        if Patient.query.count() == 0:
            print("\n➕ إضافة بيانات المرضى...")
            
            patients = [
                Patient(
                    first_name='محمد',
                    middle_name='عبدالله',
                    last_name='الزيد',
                    gender='ذكر',
                    birth_date=datetime.now() - timedelta(days=365*30),
                    phone_number='0501234567'
                ),
                Patient(
                    first_name='سارة',
                    middle_name='علي',
                    last_name='العتيبي',
                    gender='أنثى',
                    birth_date=datetime.now() - timedelta(days=365*25),
                    phone_number='0557654321'
                ),
                Patient(
                    first_name='خالد',
                    middle_name='سالم',
                    last_name='العمري',
                    gender='ذكر',
                    birth_date=datetime.now() - timedelta(days=365*40),
                    phone_number='0567890123'
                )
            ]
            
            for patient in patients:
                db.session.add(patient)
            
            db.session.commit()
            print("✅ تم إضافة 3 مرضى")
            
            # 3. إضافة ملفات طبية للمرضى
            all_patients = Patient.query.all()
            blood_types = ['O+', 'A+', 'B+']
            
            for i, patient in enumerate(all_patients):
                # التحقق من عدم وجود ملف طبي للمريض
                existing_profile = MedicalProfile.query.filter_by(patient_id=patient.id).first()
                if not existing_profile:
                    profile = MedicalProfile(
                        patient_id=patient.id,
                        blood_type=blood_types[i % len(blood_types)],
                        height=165 + (i * 5),
                        weight=65 + (i * 3),
                        chronic_diseases='سكري' if i == 0 else '',
                        allergies='حساسية البنسلين' if i == 1 else '',
                        general_notes=''
                    )
                    db.session.add(profile)
                    print(f"✅ تم إنشاء ملف طبي للمريض: {patient.full_name()}")
            
            db.session.commit()
            
            # 4. إضافة حالات مرضية
            doctor = User.query.filter_by(username='doctor1').first()
            if doctor:
                profiles = MedicalProfile.query.all()
                for i, profile in enumerate(profiles):
                    case = MedicalCase(
                        medical_profile_id=profile.id,
                        doctor_id=doctor.id,
                        case_date=datetime.now() - timedelta(days=30 * (i + 1)),
                        case_description=f'فحص روتيني للمريض {i+1}',
                        treatment_details='فحص طبي شامل، قياس ضغط الدم',
                        prescribed_medications='فيتامين د 1000 وحدة يومياً',
                        lab_tests_and_results='تحليل دم - النتائج طبيعية',
                        visited_facilities='العيادة الخارجية',
                        additional_notes='يحتاج متابعة خلال شهر'
                    )
                    db.session.add(case)
                
                db.session.commit()
                print("✅ تم إضافة حالات مرضية")
        
        else:
            patient_count = Patient.query.count()
            print(f"\n⚠️  لديك بالفعل {patient_count} مريض في قاعدة البيانات")
            print("   لن يتم إضافة بيانات جديدة للمرضى")
        
        print("\n" + "="*50)
        print("🎉 اكتمل إعداد البذور بنجاح!")
        print("="*50)
        print("\n🔑 بيانات الدخول المتاحة:")
        print("   👑 المدير:     admin / admin123")
        print("   👨‍⚕️ الطبيب:    doctor1 / doctor123")
        print("   👨‍💼 المساعد:   assistant1 / assistant123")
        print("\n🚀 لتشغيل التطبيق:")
        print("   python run.py")
        print("="*50)

if __name__ == '__main__':
    seed_database()