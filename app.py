"""
app.py - ملف التشغيل الرئيسي للتطبيق
تشغيل: gunicorn app:app
"""

import os
import sys
from dotenv import load_dotenv

# إصلاح مشكلة psycopg مع Python 3.13
os.environ['SQLALCHEMY_PSYCOPG_IMPL'] = 'psycopg'

# تحميل متغيرات البيئة
load_dotenv()

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# استيراد التطبيق
from app import create_app

# إنشاء التطبيق
app = create_app()

# للتشغيل المحلي
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)