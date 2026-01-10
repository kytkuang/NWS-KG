from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models.user import db, User
from utils.security import (
    generate_token, 
    verify_token, 
    validate_email, 
    validate_username,
    validate_password
)

# 创建蓝图
bp = Blueprint('auth', __name__)

@bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        
        # 验证必要字段
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # 验证字段
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
        
        db.session.add(new_user)
        db.session.commit()
        
        # 生成令牌
        token = generate_token(new_user.id, new_user.username)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        identifier = data.get('username', '').strip()  # 可以是用户名或邮箱
        password = data.get('password', '').strip()
        
        if not identifier or not password:
            return jsonify({'success': False, 'message': '请提供用户名/邮箱和密码'}), 400
        
        # 根据邮箱或用户名查找用户
        if '@' in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()
        
        # 验证用户
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        if not user.is_active:
            return jsonify({'success': False, 'message': '账户已被禁用'}), 403
        
        if not user.check_password(password):
            return jsonify({'success': False, 'message': '密码错误'}), 401
        
        # 更新登录信息
        user.update_login_info()
        db.session.commit()
        
        # 生成令牌
        token = generate_token(user.id, user.username)
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    try:
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供认证令牌'}), 401
        
        token = auth_header.split(' ')[1]
        
        # 验证令牌
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 401

@bp.route('/auth/check-username/<username>', methods=['GET'])
def check_username(username):
    """检查用户名是否可用"""
    exists = User.query.filter_by(username=username.strip()).first() is not None
    return jsonify({
        'success': True,
        'available': not exists,
        'exists': exists
    })

@bp.route('/auth/check-email/<email>', methods=['GET'])
def check_email(email):
    """检查邮箱是否可用"""
    exists = User.query.filter_by(email=email.strip()).first() is not None
    return jsonify({
        'success': True,
        'available': not exists,
        'exists': exists
    })

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出（客户端应删除令牌）"""
    return jsonify({
        'success': True,
        'message': '已登出'
    })

@bp.route('/auth/update-profile', methods=['PUT'])
def update_profile():
    """更新用户资料"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未认证'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': '无更新数据'}), 400
        
        # 更新允许的字段
        if 'email' in data and data['email'] != user.email:
            # 验证新邮箱是否可用
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': '邮箱已被使用'}), 409
            user.email = data['email']
        
        # 更新密码（如果提供）
        if 'old_password' in data and 'new_password' in data:
            if user.check_password(data['old_password']):
                is_valid, msg = validate_password(data['new_password'])
                if not is_valid:
                    return jsonify({'success': False, 'message': msg}), 400
                user.set_password(data['new_password'])
            else:
                return jsonify({'success': False, 'message': '原密码错误'}), 401
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '资料更新成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500