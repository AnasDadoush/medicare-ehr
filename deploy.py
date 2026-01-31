# deploy.py
#!/usr/bin/env python3
"""
نص نشر MediCare EHR System
تشغيل: python deploy.py
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(command, description):
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def setup_project():
    """إعداد المشروع بالكامل"""
    
    print_header("🚀 MediCare EHR Deployment Setup")
    
    # 1. تحميل متغيرات البيئة
    print("\n📁 Loading environment variables...")
    load_dotenv()
    
    # 2. تثبيت المتطلبات
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # 3. إنشاء قاعدة بيانات محلية (إذا لم تكن موجودة)
    if os.environ.get('FLASK_ENV') == 'development':
        print("\n🗄️ Setting up local database...")
        
        # يمكنك إضافة أوامر لإنشاء قاعدة بيانات PostgreSQL محلية هنا
        print("Note: Ensure PostgreSQL is running locally")
        print("Default connection: postgresql://postgres:0812@localhost:5432/medicare_ehr")
    
    # 4. إنشاء الجداول
    print("\n🛠️ Creating database tables...")
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        from app import create_app
        from app import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database tables created!")
            
            # إضافة مستخدم admin
            from app.models.user import User
            
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    full_name='مدير النظام',
                    username='admin',
                    role='ADMIN'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("👤 Admin user created (admin/admin123)")
    
    except Exception as e:
        print(f"⚠️ Note: {e}")
        print("This might be normal if tables already exist")
    
    # 5. إنشاء ملفات Flask-Migrate
    print("\n📦 Setting up database migrations...")
    if os.path.exists("migrations"):
        print("✅ Migrations folder already exists")
    else:
        run_command("flask db init", "Initializing migrations")
        run_command("flask db migrate -m 'Initial tables'", "Creating migration")
        run_command("flask db upgrade", "Applying migration")
    
    print_header("✅ Setup Completed Successfully!")
    
    print("\n📋 Next Steps:")
    print("1. 🔧 Configure environment variables in .env file")
    print("2. 🗄️  Ensure database is running")
    print("3. 🚀 Run the application: python run.py")
    print("4. 🌐 Open browser: http://localhost:5000")
    print("5. 🔑 Login with: admin / admin123")
    print("\n📦 For Render deployment:")
    print("   - Add DATABASE_URL from Render dashboard")
    print("   - Add SECRET_KEY environment variable")
    print("   - Connect your GitHub repository")
    
    return True

if __name__ == '__main__':
    setup_project()