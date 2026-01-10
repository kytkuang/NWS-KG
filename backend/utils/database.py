from models.user import db

def init_db(app):
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表已创建")
        
        # 可选：创建默认管理员账户
        create_default_admin()

def create_default_admin():
    """创建默认管理员账户（如果不存在）"""
    from models.user import User
    admin_email = "admin@cybersecurity.com"
    
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            username="admin",
            email=admin_email,
            password="admin123"  # 生产环境请修改！
        )
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        print("✅ 默认管理员账户已创建")