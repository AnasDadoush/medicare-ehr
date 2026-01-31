import os
from datetime import timedelta

class Config:
    # 🔴 المفاتيح السرية
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 🔴 إعدادات الجلسات
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False  # True في production مع HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 🔴 تكوين قاعدة البيانات (مع دعم psycopg3)
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    # معالجة رابط قاعدة البيانات
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://')
        elif DATABASE_URL.startswith('postgresql://'):
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # للتطوير المحلي
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:0812@localhost:5432/medicare_ehr'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # حدود الرفع
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # التحكم في التصحيح
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # قاعدة بيانات محلية للتطوير
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:0812@localhost:5432/medicare_ehr'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY
    SESSION_COOKIE_SECURE = True
    
    # استخدام DATABASE_URL من متغيرات البيئة
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://')
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # استخدام SQLite كبديل
        app_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(app_dir, 'instance', 'medicare.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'testing-secret-key'