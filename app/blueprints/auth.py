from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for, session
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return render_template('auth/login.html', error='اسم المستخدم أو كلمة المرور غير صحيحة')
    
    if not user.is_active:
        return render_template('auth/login.html', error='الحساب غير نشط')
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['full_name'] = user.full_name
    
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))