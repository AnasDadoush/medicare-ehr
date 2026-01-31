from flask import Flask, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 🔴 إعدادات الجلسات
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-very-secret-key-here-change-in-production')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_COOKIE_SECURE'] = False  # True في production مع HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # 🔴 تحميل التكوين المناسب
    from config import DevelopmentConfig, ProductionConfig
    
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions with app
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    migrate.init_app(app, db)
    
    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.medical_case import medical_cases_bp
    from .blueprints.medical_profile import medical_profiles_bp
    from .blueprints.users import users_bp
    from .blueprints.patients import patients_bp
    from .blueprints.appointments import appointments_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medical_cases_bp)
    app.register_blueprint(medical_profiles_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(appointments_bp)
    
    # إضافة route أساسي للصفحة الرئيسية
    @app.route('/')
    def home():
        return redirect('/login')
    
    # إنشاء الجداول عند أول طلب (للتطوير)
    @app.before_request
    def create_tables_on_first_request():
        """إنشاء الجداول عند أول طلب إذا لم تكن موجودة"""
        if not hasattr(app, 'tables_created'):
            with app.app_context():
                try:
                    # إنشاء الجداول فقط إذا لم تكن موجودة
                    from sqlalchemy import inspect
                    inspector = inspect(db.engine)
                    existing_tables = inspector.get_table_names()
                    
                    if not existing_tables:
                        db.create_all()
                        app.logger.info("✅ Database tables created")
                    
                    app.tables_created = True
                except Exception as e:
                    app.logger.warning(f"⚠️ Table creation note: {e}")
    
    return app