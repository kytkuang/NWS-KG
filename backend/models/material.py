from datetime import datetime
from .user import db


class Material(db.Model):
    """
    学习资料模型
    用于存储学习相关的PDF文件等资料
    """
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # 资料标题
    description = db.Column(db.Text, default="")  # 资料描述
    file_path = db.Column(db.String(500), nullable=False)  # 文件存储路径
    file_name = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_size = db.Column(db.Integer, default=0)  # 文件大小（字节）
    file_type = db.Column(db.String(50), default="pdf")  # 文件类型，默认pdf
    component_name = db.Column(db.String(100), nullable=True, index=True)  # 关联的Vue组件名称（知识点）
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)  # 创建者ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    creator = db.relationship("User", foreign_keys=[created_by])

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "component_name": self.component_name,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "creator": {
                "id": self.creator.id,
                "username": self.creator.username
            } if self.creator else None
        }
