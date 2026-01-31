# create_tables.py
"""
إنشاء الجداول باستخدام db من التطبيق الحقيقي
تشغيل: python create_tables.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    """الدالة الرئيسية لإنشاء الجداول"""
    print("="*60)
    print("🗄️  Creating Database Tables")
    print("="*60)

    # إضافة المسار
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # استيراد التطبيق الحقيقي
    from app import create_app, db

    # إنشاء التطبيق
    app = create_app()

    with app.app_context():
        try:
            print("📊 Creating all tables...")
            
            # إنشاء جميع الجداول
            db.create_all()
            
            print("✅ Tables created successfully!")
            
            # التحقق من الجداول المنشأة
            from sqlalchemy import inspect
            
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Tables created ({len(tables)}):")
            for table in tables:
                print(f"   • {table}")
            
            # التحقق من اتصال قاعدة البيانات
            try:
                result = db.session.execute('SELECT 1').scalar()
                print(f"\n🔗 Database connection: ✅ Active (test query returned: {result})")
            except Exception as e:
                print(f"\n⚠️ Database connection test failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_tables()
    
    if success:
        print("\n" + "="*60)
        print("✅ Database tables created successfully!")
        print("="*60)
        print("\n📋 Next steps:")
        print("1. Add sample data: python seed_data.py")
        print("2. Run the app: python run.py")
        print("3. Open: http://localhost:5000")
        print("="*60)
    else:
        print("\n❌ Failed to create tables")