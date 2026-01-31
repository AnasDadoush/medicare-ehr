# run.py - يجب أن يكون هكذا بالضبط
import os
import sys
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app import create_app
    app = create_app()  # ⚠️ هذا السطر أهم شيء
    
    if __name__ == '__main__':
        print("Starting MediCare EHR...")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
