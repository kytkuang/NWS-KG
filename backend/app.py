from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import DATABASE_CONFIG, JWT_CONFIG, FLASK_CONFIG
from config.mysql_config import MySQLConfig
from models.user import db
from routes.auth import bp as auth_bp
from routes.graph import bp as graph_bp
from routes.knowledge import bp as knowledge_bp
from routes.admin import bp as admin_bp
from utils.database import init_db

app = Flask(__name__)

# 加载配置
app.config.from_object(MySQLConfig)
app.config['SECRET_KEY'] = JWT_CONFIG['SECRET_KEY']

# 启用CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 初始化数据库
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(graph_bp, url_prefix="/api")
app.register_blueprint(knowledge_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")

@app.route("/")
def home():
    return jsonify({
        "project": "网络安全知识图谱平台",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "me": "GET /api/auth/me",
                "check_username": "GET /api/auth/check-username/<username>",
                "check_email": "GET /api/auth/check-email/<email>"
            },
            "admin": {
                "users": "GET /api/admin/users",
                "create_user": "POST /api/admin/users",
                "get_user": "GET /api/admin/users/<user_id>",
                "update_user": "PUT /api/admin/users/<user_id>",
                "delete_user": "DELETE /api/admin/users/<user_id>",
                "reset_password": "POST /api/admin/users/<user_id>/reset-password",
                "stats": "GET /api/admin/stats"
            },
            "graph": {
                "nodes": "GET /api/graph/nodes",
                "edges": "GET /api/graph/edges"
            }
        }
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        db.session.execute('SELECT 1')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # 实际应该用datetime.now()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route("/api/init-db", methods=["POST"])
def initialize_database():
    """初始化数据库表（仅开发环境使用）"""
    try:
        init_db(app)
        return jsonify({
            "success": True,
            "message": "数据库初始化完成"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"数据库初始化失败: {str(e)}"
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "请求的资源不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "服务器内部错误"
    }), 500

if __name__ == "__main__":
    # 初始化数据库表
    with app.app_context():
        db.create_all()
        print("✅ 数据库表已初始化")
    
    # 启动应用
    print(f"🚀 服务器启动: http://0.0.0.0:5005")
    print(f"📊 API文档: http://0.0.0.0:5005/")
    app.run(host="0.0.0.0", port=5005, debug=True)