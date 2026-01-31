# app/__init__.py
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
    
    # 🔴 تكوين قاعدة البيانات
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0812@localhost:5432/test_DB'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
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
    
    return app  # ⚠️ لا يوجد before_first_request هنا