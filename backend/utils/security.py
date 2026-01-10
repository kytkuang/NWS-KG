import jwt
import datetime
from flask import current_app

def generate_token(user_id, username, expires_in=86400):
    """生成JWT令牌 (默认24小时过期)"""
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
            'iat': datetime.datetime.utcnow()
        }
        # 使用settings.py中的SECRET_KEY
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        raise Exception(f"生成令牌失败: {str(e)}")

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("令牌已过期")
    except jwt.InvalidTokenError:
        raise Exception("无效的令牌")

def validate_email(email):
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """验证用户名格式（3-20位字母数字下划线）"""
    import re
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """验证密码强度（至少6位）"""
    if len(password) < 6:
        return False, "密码至少需要6位"
    
    # 可选：添加更多强度检查
    # if not any(c.isupper() for c in password):
    #     return False, "密码应包含至少一个大写字母"
    # if not any(c.isdigit() for c in password):
    #     return False, "密码应包含至少一个数字"
    
    return True, "密码符合要求"