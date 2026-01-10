from .user import db, User
from .knowledge import KnowledgeNode, KnowledgeRelation

# 导出所有模型
__all__ = ["db", "User", "KnowledgeNode", "KnowledgeRelation"]