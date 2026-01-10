from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from functools import wraps
from models.user import db, User
from utils.security import (
    generate_token,
    verify_token,
    validate_email,
    validate_username,
    validate_password
)

# 创建蓝图
bp = Blueprint('admin', __name__)

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未认证'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': '无效令牌'}), 401

        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        if not user.is_admin:
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403

        return f(user, *args, **kwargs)
    return decorated_function

@bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users(admin_user):
    """获取用户列表（管理员专用）"""
    try:
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()
        role = request.args.get('role', '').strip()

        # 构建查询
        query = User.query

        # 搜索功能
        if search:
            if '@' in search:
                # 按邮箱搜索
                query = query.filter(User.email.ilike(f'%{search}%'))
            else:
                # 按用户名搜索
                query = query.filter(User.username.ilike(f'%{search}%'))

        # 状态筛选
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)

        # 角色筛选
        if role == 'admin':
            query = query.filter(User.is_admin == True)
        elif role == 'user':
            query = query.filter(User.is_admin == False)

        # 分页 - 管理员永远置顶
        pagination = query.order_by(User.is_admin.desc(), User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        users = []
        for user in pagination.items:
            users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count,
                'study_progress': user.study_progress
            })

        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户列表失败: {str(e)}'}), 500

@bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(admin_user, user_id):
    """获取单个用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count,
                'study_progress': user.study_progress
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500

@bp.route('/admin/users', methods=['POST'])
@admin_required
def create_user(admin_user):
    """创建新用户（管理员专用）"""
    try:
        data = request.json

        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        is_admin = data.get('is_admin', False)
        is_active = data.get('is_active', True)

        # 验证必要字段
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': '请填写所有必填项'}), 400

        # 验证用户名格式
        if not validate_username(username):
            return jsonify({'success': False, 'message': '用户名格式无效（3-20位字母数字下划线）'}), 400

        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({'success': False, 'message': '邮箱格式无效'}), 400

        # 验证密码强度
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '用户名已存在'}), 409

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': '邮箱已注册'}), 409

        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            password=password
        )
        new_user.is_admin = is_admin
        new_user.is_active = is_active

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建用户失败: {str(e)}'}), 500

@bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(admin_user, user_id):
    """更新用户信息（管理员专用）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '无更新数据'}), 400

        # 更新邮箱
        if 'email' in data and data['email'] != user.email:
            if not validate_email(data['email']):
                return jsonify({'success': False, 'message': '邮箱格式无效'}), 400

            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'success': False, 'message': '邮箱已被使用'}), 409

            user.email = data['email']

        # 更新密码（如果提供）
        if 'password' in data and data['password'].strip():
            is_valid, msg = validate_password(data['password'])
            if not is_valid:
                return jsonify({'success': False, 'message': msg}), 400
            user.set_password(data['password'])

        # 更新权限和状态
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])

        # 更新学习进度（如果提供）
        if 'study_progress' in data:
            user.study_progress = float(data['study_progress'])

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '用户信息更新成功',
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新用户信息失败: {str(e)}'}), 500

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(admin_user, user_id):
    """删除用户（管理员专用）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 防止删除自己
        if user.id == admin_user.id:
            return jsonify({'success': False, 'message': '不能删除自己的账号'}), 400

        # 检查是否为强制删除
        force_delete = request.args.get('force', '').lower() == 'true'

        if force_delete:
            # 真正删除用户
            db.session.delete(user)
            message = '用户已被永久删除'
        else:
            # 软删除：将用户标记为非活跃状态
            user.is_active = False
            user.updated_at = datetime.utcnow()
            message = '用户已被停用'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除用户失败: {str(e)}'}), 500

@bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(admin_user, user_id):
    """重置用户密码（管理员专用）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        data = request.json
        new_password = data.get('password', '').strip() if data else ''

        if not new_password:
            # 生成随机密码
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for i in range(12))

        # 验证密码强度
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400

        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password  # 在生产环境中应该不返回密码
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'}), 500

@bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats(admin_user):
    """获取管理员统计信息"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        inactive_users = total_users - active_users

        # 最近注册的用户（最近7天）
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= seven_days_ago).count()

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'admin_users': admin_users,
                'recent_users': recent_users
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计信息失败: {str(e)}'}), 500