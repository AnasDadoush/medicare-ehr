# run.py
import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app import create_app
    
    # إنشاء التطبيق
    app = create_app()
    
    @app.cli.command("create-db")
    def create_database_tables():
        """أمر CLI لإنشاء جداول قاعدة البيانات"""
        with app.app_context():
            from app import db
            from app.models.user import User
            
            try:
                print("=" * 60)
                print("🚀 Creating database tables...")
                print("=" * 60)
                
                # إنشاء جميع الجداول
                db.create_all()
                print("✅ Tables created successfully!")
                
                # إضافة مستخدم admin إذا لم يكن موجود
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin = User(
                        full_name='مدير النظام',
                        username='admin',
                        role='ADMIN'
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    print("👤 Admin user created (admin/admin123)")
                
                print("=" * 60)
                print("🎉 Database setup completed!")
                print("=" * 60)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    @app.cli.command("seed-data")
    def seed_sample_data():
        """أمر CLI لإضافة بيانات تجريبية"""
        with app.app_context():
            from app import db
            from app.models.user import User
            from app.models.patient import Patient
            from app.models.medical_profile import MedicalProfile
            
            try:
                print("=" * 60)
                print("🌱 Seeding sample data...")
                print("=" * 60)
                
                # إضافة أطباء ومساعدين
                staff = [
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
                
                for person in staff:
                    existing = User.query.filter_by(username=person['username']).first()
                    if not existing:
                        user = User(
                            full_name=person['full_name'],
                            username=person['username'],
                            role=person['role']
                        )
                        user.set_password(person['password'])
                        db.session.add(user)
                        print(f"👤 Created {person['role']}: {person['username']}")
                
                # إضافة مرضى تجريبيين
                patients = [
                    {
                        'first_name': 'محمد',
                        'last_name': 'علي',
                        'gender': 'ذكر',
                        'phone_number': '0551234567'
                    },
                    {
                        'first_name': 'فاطمة',
                        'last_name': 'خالد',
                        'gender': 'أنثى',
                        'phone_number': '0549876543'
                    },
                    {
                        'first_name': 'عبدالله',
                        'middle_name': 'سالم',
                        'last_name': 'الزيد',
                        'gender': 'ذكر',
                        'phone_number': '0501122334'
                    }
                ]
                
                for patient_data in patients:
                    existing = Patient.query.filter_by(
                        first_name=patient_data['first_name'],
                        last_name=patient_data['last_name']
                    ).first()
                    
                    if not existing:
                        patient = Patient(**patient_data)
                        db.session.add(patient)
                        db.session.flush()  # للحصول على ID
                        
                        # إنشاء ملف طبي للمريض
                        profile = MedicalProfile(patient_id=patient.id)
                        db.session.add(profile)
                        
                        print(f"👨‍⚕️ Created patient: {patient.full_name()}")
                
                db.session.commit()
                
                print("=" * 60)
                print("✅ Sample data seeded successfully!")
                print("🔑 Login credentials:")
                print("   Admin: admin / admin123")
                print("   Doctor: doctor1 / doctor123")
                print("   Assistant: assistant1 / assistant123")
                print("=" * 60)
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    if __name__ == '__main__':
        print("\n" + "="*50)
        print(" MediCare EHR System - Session Based")
        print("="*50)
        print(f" Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f" Database: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1]}")
        
        # التحقق من اتصال قاعدة البيانات
        with app.app_context():
            try:
                from app import db
                db.session.execute('SELECT 1')
                print("✅ Database: Connected")
            except Exception as e:
                print(f"❌ Database Error: {e}")
        
        print("="*50)
        print(" Starting server...")
        
        host = '0.0.0.0'
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        app.run(debug=debug, host=host, port=port)
        
except Exception as e:
    print(f"❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()