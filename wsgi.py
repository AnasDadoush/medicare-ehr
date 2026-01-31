# wsgi.py
import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إضافة المسار
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()