from .user import db, User
from .knowledge import KnowledgeNode, KnowledgeRelation
from .learning_path import LearningPath, LearningPathNode, UserLearningPath, UserLearningProgress
from .material import Material

# 导出所有模型
__all__ = ["db", "User", "KnowledgeNode", "KnowledgeRelation", "LearningPath", "LearningPathNode", "UserLearningPath", "UserLearningProgress", "Material"]