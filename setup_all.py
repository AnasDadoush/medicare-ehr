# setup_all.py
"""
ملف واحد لإنشاء الجداول وإضافة البيانات
تشغيل: python setup_all.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def setup_all():
    """تهيئة كل شيء"""
    print("="*60)
    print("🚀 Complete Database Setup")
    print("="*60)
    
    # إضافة المسار
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    try:
        from app import create_app, db
        
        # 1. إنشاء التطبيق والجداول
        app = create_app()
        
        with app.app_context():
            print("📊 Step 1: Creating tables...")
            db.create_all()
            print("✅ Tables created")
            
            # 2. التحقق من الجداول
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables found: {len(tables)}")
            
            # 3. إضافة بيانات أساسية إذا كانت الجداول فارغة
            if 'users' in tables:
                from app.models.user import User
                
                # تحقق إذا كان هناك مستخدمين
                user_count = User.query.count()
                
                if user_count == 0:
                    print("\n👤 Step 2: Adding admin user...")
                    
                    admin = User(
                        full_name='مدير النظام',
                        username='admin',
                        role='ADMIN'
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    
                    print("✅ Admin user created: admin / admin123")
                else:
                    print(f"✅ Users already exist: {user_count} users")
            
            print("\n" + "="*60)
            print("✅ Setup completed!")
            print("="*60)
            print("\n🚀 Run the app: python run.py")
            print("🌐 Open: http://localhost:5000")
            print("🔑 Login: admin / admin123")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    setup_all()