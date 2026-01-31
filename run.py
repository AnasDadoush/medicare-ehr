"""
run.py - للتشغيل المحلي فقط
تشغيل: python run.py
"""

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
    
    app = create_app()
    
    if __name__ == '__main__':
        print("\n" + "="*50)
        print(" MediCare EHR System - Development Mode")
        print("="*50)
        print(f" Environment: {os.environ.get('FLASK_ENV', 'development')}")
        
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        app.run(debug=debug, host='0.0.0.0', port=port)
        
except Exception as e:
    print(f"❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()