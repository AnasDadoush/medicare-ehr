# config.py
import os
from datetime import timedelta

class Config:
    # 🔴 المفاتيح السرية - ضرورية للجلسات
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 🔴 إعدادات الجلسات
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False  # True في production مع HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 🔴 تكوين قاعدة البيانات
    # معالجة رابط Render الخاص
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or \
        'postgresql://postgres:0812@localhost:5432/test_DB'
    
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
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:0812@localhost:5432/test_DB'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY
    SESSION_COOKIE_SECURE = True
    
    # استخدام DATABASE_URL من متغيرات البيئة
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://'
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'testing-secret-key'