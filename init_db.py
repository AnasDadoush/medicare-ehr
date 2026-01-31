# init_db.py - الملف المعدل
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    
    print("="*60)
    print("🗄️  Database Initialization")
    print("="*60)
    
    # إضافة مسار المشروع
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    try:
        # استيراد مباشر بدون استخدام create_app
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from app.models.user import User
        from app.models.patient import Patient
        from app.models.medical_profile import MedicalProfile
        from app.models.medical_case import MedicalCase
        from app.models.appointment import Appointment
        
        # إنشاء تطبيق Flask مؤقت
        app = Flask(__name__)
        
        # تكوين قاعدة البيانات مباشرة
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            db_url = 'postgresql://postgres:0812@localhost:5432/medicare_ehr'
        
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'temp-secret-for-db-init'
        
        # إنشاء كائن db
        db = SQLAlchemy(app)
        
        print(f"📊 Database: {db_url.split('@')[-1]}")
        
        # استيراد النماذج مرة أخرى بعد تهيئة db
        from app.models.user import User
        from app.models.patient import Patient
        from app.models.medical_profile import MedicalProfile
        from app.models.medical_case import MedicalCase
        from app.models.appointment import Appointment
        
        print("\n📊 Creating tables...")
        
        # إنشاء جميع الجداول
        with app.app_context():
            db.create_all()
            print("✅ Tables created successfully!")
            
            return True, db, app
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def seed_database(db, app):
    """إضافة بيانات تجريبية"""
    
    print("\n🌱 Seeding sample data...")
    
    try:
        from datetime import datetime, timedelta
        
        with app.app_context():
            # 1. إضافة المستخدمين
            print("   👤 Adding users...")
            users_data = [
                {'full_name': 'مدير النظام', 'username': 'admin', 'password': 'admin123', 'role': 'ADMIN'},
                {'full_name': 'د. أحمد محمد', 'username': 'doctor1', 'password': 'doctor123', 'role': 'DOCTOR'},
                {'full_name': 'د. سارة عبدالله', 'username': 'doctor2', 'password': 'doctor123', 'role': 'DOCTOR'},
                {'full_name': 'مساعد العيادة', 'username': 'assistant1', 'password': 'assistant123', 'role': 'ASSISTANT'}
            ]
            
            for user_data in users_data:
                from app.models.user import User
                existing = User.query.filter_by(username=user_data['username']).first()
                if not existing:
                    user = User(
                        full_name=user_data['full_name'],
                        username=user_data['username'],
                        role=user_data['role']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"      Created: {user_data['username']}")
            
            db.session.commit()
            
            # 2. إضافة المرضى
            print("   👨‍⚕️ Adding patients...")
            patients_data = [
                {'first_name': 'محمد', 'last_name': 'علي', 'gender': 'ذكر', 'phone': '0551234567'},
                {'first_name': 'فاطمة', 'last_name': 'خالد', 'gender': 'أنثى', 'phone': '0549876543'},
                {'first_name': 'عبدالله', 'last_name': 'الزيد', 'gender': 'ذكر', 'phone': '0501122334'}
            ]
            
            for patient_data in patients_data:
                from app.models.patient import Patient
                existing = Patient.query.filter_by(
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name']
                ).first()
                
                if not existing:
                    patient = Patient(
                        first_name=patient_data['first_name'],
                        last_name=patient_data['last_name'],
                        gender=patient_data['gender'],
                        phone_number=patient_data['phone']
                    )
                    db.session.add(patient)
                    print(f"      Created: {patient.full_name()}")
            
            db.session.commit()
            
            # 3. إضافة ملفات طبية
            print("   📁 Adding medical profiles...")
            patients = Patient.query.all()
            
            for i, patient in enumerate(patients[:3]):
                from app.models.medical_profile import MedicalProfile
                existing = MedicalProfile.query.filter_by(patient_id=patient.id).first()
                
                if not existing:
                    blood_types = ['O+', 'A+', 'B+']
                    heights = [175, 162, 180]
                    weights = [72.5, 58.0, 85.0]
                    diseases = ['سكري النوع الثاني', 'ضغط الدم', 'كولسترول']
                    allergies = ['حساسية من البنسلين', 'لا توجد', 'حساسية من الغبار']
                    
                    profile = MedicalProfile(
                        patient_id=patient.id,
                        blood_type=blood_types[i],
                        height=heights[i],
                        weight=weights[i],
                        chronic_diseases=diseases[i],
                        allergies=allergies[i]
                    )
                    db.session.add(profile)
                    print(f"      Created profile for: {patient.full_name()}")
            
            db.session.commit()
            
            # 4. إضافة حالات مرضية
            print("   🏥 Adding medical cases...")
            profiles = MedicalProfile.query.all()
            doctors = [u for u in User.query.filter_by(role='DOCTOR').all()]
            
            if profiles and doctors:
                from app.models.medical_case import MedicalCase
                
                case1 = MedicalCase(
                    medical_profile_id=profiles[0].id,
                    doctor_id=doctors[0].id,
                    case_date=datetime.now() - timedelta(days=10),
                    case_description='زيارة دورية لفحص السكري',
                    treatment_details='ضبط جرعة الإنسولين، نصح بممارسة الرياضة'
                )
                db.session.add(case1)
                print(f"      Created medical case for profile ID: {profiles[0].id}")
            
            db.session.commit()
            
            print("✅ Data seeded successfully!")
            
            # عرض الإحصائيات
            print(f"\n📊 Database Statistics:")
            print(f"   👥 Users: {User.query.count()}")
            print(f"   👨‍⚕️ Patients: {Patient.query.count()}")
            print(f"   📁 Medical Profiles: {MedicalProfile.query.count()}")
            print(f"   🏥 Medical Cases: {MedicalCase.query.count()}")
            print(f"   📅 Appointments: {0}")  # لم ننشئ مواعيد بعد
            
            return True
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # تهيئة الجداول
    success, db, app = init_database()
    
    if success:
        # إضافة البيانات
        seed_database(db, app)
        
        print("\n" + "="*60)
        print("✅ Database setup completed!")
        print("="*60)
        print("\n🔑 Login credentials:")
        print("   Admin:     admin / admin123")
        print("   Doctor:    doctor1 / doctor123")
        print("   Assistant: assistant1 / assistant123")
        print("\n🚀 Run the app: python run.py")
        print("🌐 Then open: http://localhost:5000")
        print("="*60)