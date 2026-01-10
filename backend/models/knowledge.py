from datetime import datetime

from .user import db


class KnowledgeNode(db.Model):
    """
    知识点实体
    用于管理网络安全领域的概念 / 技术 / 攻击手法等。
    """

    __tablename__ = "knowledge_nodes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, default="concept")  # 如 tactic / technique / vulnerability / course
    description = db.Column(db.Text, default="")
    source = db.Column(db.String(50), nullable=False, default="custom")  # mitre / custom / other
    neo4j_id = db.Column(db.String(128), nullable=True, index=True)  # 关联到 Neo4j 中对应节点的业务 id

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "source": self.source,
            "neo4j_id": self.neo4j_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class KnowledgeRelation(db.Model):
    """
    知识点之间的关系元数据
    例如：依赖（prerequisite）、包含（contains）、关联（related）等。
    """

    __tablename__ = "knowledge_relations"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    target_id = db.Column(db.Integer, db.ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    relation_type = db.Column(db.String(50), nullable=False, default="related")
    description = db.Column(db.String(255), default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    source = db.relationship("KnowledgeNode", foreign_keys=[source_id], backref="out_relations")
    target = db.relationship("KnowledgeNode", foreign_keys=[target_id], backref="in_relations")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

