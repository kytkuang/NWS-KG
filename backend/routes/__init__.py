# 导出所有路由蓝图
from .graph import bp as graph_bp
from .auth import bp as auth_bp

__all__ = ['graph_bp', 'auth_bp']