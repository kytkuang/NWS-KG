from datetime import datetime
from .user import db


class LearningPath(db.Model):
    """
    学习路径模板
    可以是系统预设的基础路径，也可以是用户自定义路径
    """
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(100), default="general")  # general / cybersecurity / network / etc.
    is_system = db.Column(db.Boolean, default=False)  # 是否为系统预设路径
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)  # 创建者ID，系统路径为NULL
    difficulty = db.Column(db.String(50), default="beginner")  # beginner / intermediate / advanced
    estimated_duration = db.Column(db.Integer, default=0)  # 预计学习时长（小时）
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    nodes = db.relationship("LearningPathNode", back_populates="path", cascade="all, delete-orphan", order_by="LearningPathNode.order")
    user_paths = db.relationship("UserLearningPath", back_populates="path", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "is_system": self.is_system,
            "created_by": self.created_by,
            "difficulty": self.difficulty,
            "estimated_duration": self.estimated_duration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "node_count": len(self.nodes) if self.nodes else 0
        }


class LearningPathNode(db.Model):
    """
    学习路径中的节点（知识点）
    表示路径中的一个学习步骤
    """
    __tablename__ = "learning_path_nodes"

    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"), nullable=False, index=True)
    knowledge_node_id = db.Column(db.Integer, db.ForeignKey("knowledge_nodes.id"), nullable=True, index=True)  # 关联的知识点ID
    node_name = db.Column(db.String(255), nullable=False)  # 节点名称（如果knowledge_node_id为空，则使用此字段）
    node_type = db.Column(db.String(100), default="knowledge")  # knowledge / course / practice / exam
    description = db.Column(db.Text, default="")
    order = db.Column(db.Integer, nullable=False, default=0)  # 在路径中的顺序
    prerequisites = db.Column(db.Text, default="")  # JSON格式，存储前置节点ID列表
    estimated_time = db.Column(db.Integer, default=0)  # 预计学习时间（分钟）
    resources = db.Column(db.Text, default="")  # JSON格式，存储学习资源链接
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联关系
    path = db.relationship("LearningPath", back_populates="nodes")
    knowledge_node = db.relationship("KnowledgeNode", foreign_keys=[knowledge_node_id])
    user_progress = db.relationship("UserLearningProgress", back_populates="path_node", cascade="all, delete-orphan")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "path_id": self.path_id,
            "knowledge_node_id": self.knowledge_node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "description": self.description,
            "order": self.order,
            "prerequisites": json.loads(self.prerequisites) if self.prerequisites else [],
            "estimated_time": self.estimated_time,
            "resources": json.loads(self.resources) if self.resources else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "knowledge_node": self.knowledge_node.to_dict() if self.knowledge_node else None
        }


class UserLearningPath(db.Model):
    """
    用户的学习路径实例
    用户可以选择一个学习路径模板，并开始学习
    """
    __tablename__ = "user_learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"), nullable=False, index=True)
    progress = db.Column(db.Float, default=0.0)  # 学习进度百分比 0-100
    status = db.Column(db.String(50), default="in_progress")  # not_started / in_progress / completed / paused
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自定义调整（JSON格式，存储用户对路径的调整）
    custom_adjustments = db.Column(db.Text, default="")  # 例如：跳过某些节点、调整顺序等

    # 关联关系
    path = db.relationship("LearningPath", back_populates="user_paths")
    progress_records = db.relationship("UserLearningProgress", back_populates="user_path", cascade="all, delete-orphan")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "path_id": self.path_id,
            "progress": self.progress,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "custom_adjustments": json.loads(self.custom_adjustments) if self.custom_adjustments else {},
            "path": self.path.to_dict() if self.path else None
        }


class UserLearningProgress(db.Model):
    """
    用户学习进度记录
    记录用户在每个学习路径节点上的学习情况
    """
    __tablename__ = "user_learning_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    user_path_id = db.Column(db.Integer, db.ForeignKey("user_learning_paths.id"), nullable=False, index=True)
    path_node_id = db.Column(db.Integer, db.ForeignKey("learning_path_nodes.id"), nullable=False, index=True)
    status = db.Column(db.String(50), default="not_started")  # not_started / in_progress / completed / skipped
    completion_percentage = db.Column(db.Float, default=0.0)  # 节点完成百分比 0-100
    time_spent = db.Column(db.Integer, default=0)  # 已学习时间（分钟）
    notes = db.Column(db.Text, default="")  # 学习笔记
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user_path = db.relationship("UserLearningPath", back_populates="progress_records")
    path_node = db.relationship("LearningPathNode", back_populates="user_progress")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_path_id": self.user_path_id,
            "path_node_id": self.path_node_id,
            "status": self.status,
            "completion_percentage": self.completion_percentage,
            "time_spent": self.time_spent,
            "notes": self.notes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "path_node": self.path_node.to_dict() if self.path_node else None
        }
