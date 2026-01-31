# test_local_db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_local_connection():
    """اختبار اتصال قاعدة البيانات المحلية"""
    
    print("🔍 Testing local database connection...")
    
    db_url = os.environ.get('DATABASE_URL', '')
    print(f"Database URL: {db_url}")
    
    try:
        # تحليل رابط قاعدة البيانات
        if db_url.startswith('postgresql://'):
            # تنسيق: postgresql://username:password@host:port/database
            db_url = db_url.replace('postgresql://', '')
            parts = db_url.split('@')
            credentials = parts[0].split(':')
            host_port_db = parts[1].split('/')
            host_port = host_port_db[0].split(':')
            
            conn_params = {
                'host': host_port[0],
                'port': host_port[1] if len(host_port) > 1 else '5432',
                'database': host_port_db[1],
                'user': credentials[0],
                'password': credentials[1] if len(credentials) > 1 else ''
            }
            
            print(f"\nConnection parameters:")
            print(f"  Host: {conn_params['host']}")
            print(f"  Port: {conn_params['port']}")
            print(f"  Database: {conn_params['database']}")
            print(f"  User: {conn_params['user']}")
            
            # محاولة الاتصال
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            
            # اختبار الاتصال
            cursor.execute('SELECT version()')
            db_version = cursor.fetchone()
            print(f"\n✅ Connected successfully!")
            print(f"   PostgreSQL version: {db_version[0]}")
            
            # التحقق من الجداول
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            if tables:
                print(f"\n📋 Existing tables:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n📋 No tables found (database is empty)")
            
            conn.close()
            return True
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running:")
        print("   Windows: Check in Services (postgresql-x64-xx)")
        print("   Mac: brew services start postgresql")
        print("   Linux: sudo systemctl start postgresql")
        print("\n2. Check connection string in .env file")
        print("\n3. Verify database exists:")
        print("   psql -U postgres")
        print("   CREATE DATABASE medicare_ehr;")
        return False

if __name__ == '__main__':
    test_local_connection()