from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from app import db
from app.models.user import User

users_bp = Blueprint('users', __name__)

# ============== Middleware Functions ==============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'ADMIN':
            flash('صلاحيات غير كافية', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# ============== HTML Routes ==============
@users_bp.route('/users')
@login_required
@admin_required
def users_page():
    """صفحة إدارة المستخدمين"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    # 🔴 إضافة current_user من الجلسة
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('users/list.html', 
                          users=users, 
                          current_user=current_user) 
@users_bp.route('/users/create', methods=['GET'])
@login_required
@admin_required
def create_user_page():
    """صفحة إنشاء مستخدم جديد"""
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('users/create.html', current_user=current_user)
@users_bp.route('/users/<int:user_id>/edit', methods=['GET'])
@login_required
@admin_required
def edit_user_page(user_id):
    """صفحة تعديل مستخدم"""
    user = User.query.get_or_404(user_id)
    
    # 🔴 إضافة current_user
    current_user = {
        'id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'full_name': session.get('full_name')
    }
    
    return render_template('users/edit.html', user=user, current_user=current_user)

# ============== API Routes (CRUD Operations) ==============
@users_bp.route('/api/users', methods=['GET'])
@login_required
@admin_required
def list_users_api():
    """API: الحصول على قائمة المستخدمين"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/api/users', methods=['POST'])
@login_required
@admin_required
def create_user_api():
    """API: إنشاء مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['full_name', 'username', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
        
        # التحقق من عدم تكرار اسم المستخدم
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'اسم المستخدم موجود مسبقاً'}), 400
        
        # التحقق من صحة الدور
        valid_roles = ['ADMIN', 'DOCTOR', 'ASSISTANT']
        if data['role'] not in valid_roles:
            return jsonify({'success': False, 'message': 'الدور غير صالح'}), 400
        
        # إنشاء المستخدم
        user = User(
            full_name=data['full_name'],
            username=data['username'],
            role=data['role'],
            is_active=data.get('is_active', True)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user_api(user_id):
    """API: الحصول على بيانات مستخدم"""
    user = User.query.get_or_404(user_id)
    return jsonify({'success': True, 'user': user.to_dict()})

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user_api(user_id):
    """API: تحديث بيانات مستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # منع المستخدم من تعديل حسابه الخاص (للأمان)
        if user.id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'لا يمكنك تعديل حسابك الخاص من هنا'}), 400
        
        # تحديث البيانات
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'username' in data and data['username'] != user.username:
            # التحقق من عدم تكرار اسم المستخدم
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user.id:
                return jsonify({'success': False, 'message': 'اسم المستخدم موجود مسبقاً'}), 400
            user.username = data['username']
        
        if 'role' in data:
            valid_roles = ['ADMIN', 'DOCTOR', 'ASSISTANT']
            if data['role'] not in valid_roles:
                return jsonify({'success': False, 'message': 'الدور غير صالح'}), 400
            user.role = data['role']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user_api(user_id):
    """API: حذف مستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        
        # منع المستخدم من حذف حسابه الخاص
        if user.id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'لا يمكنك حذف حسابك الخاص'}), 400
        
        # منع حذف آخر مدير في النظام
        if user.role == 'ADMIN':
            admin_count = User.query.filter_by(role='ADMIN', is_active=True).count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'لا يمكن حذف آخر مدير في النظام'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المستخدم بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@users_bp.route('/api/users/<int:user_id>/toggle-status', methods=['PUT'])
@login_required
@admin_required
def toggle_user_status_api(user_id):
    """API: تفعيل/تعطيل مستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        
        # منع المستخدم من تعطيل حسابه الخاص
        if user.id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'لا يمكنك تعطيل حسابك الخاص'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'مفعل' if user.is_active else 'معطل'
        return jsonify({
            'success': True,
            'message': f'تم {status} المستخدم بنجاح',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500