# setup_render.py
"""
نص إعداد خاص للنشر على Render
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def setup_for_render():
    """إعداد خاص للنشر على Render"""
    
    print("="*60)
    print("🛠️  Render Deployment Setup")
    print("="*60)
    
    # التحقق من متغيرات البيئة
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n📋 Please set these in Render Dashboard:")
        print("   - DATABASE_URL: From your PostgreSQL database")
        print("   - SECRET_KEY: A random secret key")
        return False
    
    print("✅ Environment variables check passed")
    
    # إنشاء قاعدة بيانات
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # إنشاء الجداول
            print("\n🗄️ Creating database tables...")
            db.create_all()
            print("✅ Tables created")
            
            # إضافة مستخدم admin
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
                print("👤 Admin user created")
            
            # عرض معلومات الاتصال
            print("\n🔗 Connection Information:")
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            if '@' in db_url:
                db_info = db_url.split('@')[-1]
                print(f"   Database: {db_info}")
    
    except Exception as e:
        print(f"⚠️ Setup note: {e}")
        print("This might be normal on subsequent deployments")
    
    print("\n" + "="*60)
    print("✅ Render setup completed!")
    print("="*60)
    print("\n📋 Application should be available at:")
    print("   https://your-app.onrender.com")
    print("\n🔑 Default login: admin / admin123")
    
    return True

if __name__ == '__main__':
    setup_for_render()