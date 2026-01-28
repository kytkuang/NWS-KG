from flask import Blueprint, jsonify, request
from functools import wraps
from models.user import User
from models.knowledge import KnowledgeNode
from models.learning_path import LearningPath, LearningPathNode, UserLearningPath, UserLearningProgress
from utils.security import verify_token
import json
from datetime import datetime

bp = Blueprint("learning_path", __name__)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"code": 401, "message": "未提供认证令牌"}), 401
        
        try:
            payload = verify_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"code": 401, "message": "无效的认证令牌"}), 401
            request.user_id = user_id
        except Exception as e:
            return jsonify({"code": 401, "message": f"认证失败: {str(e)}"}), 401
        return f(*args, **kwargs)
    return wrapper


@bp.route("/learning_path/paths", methods=["GET"])
@login_required
def list_paths():
    """获取学习路径列表"""
    try:
        category = request.args.get("category", "")
        difficulty = request.args.get("difficulty", "")
        include_system = request.args.get("include_system", "true").lower() == "true"
        
        query = LearningPath.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if not include_system:
            query = query.filter_by(created_by=request.user_id)
        else:
            # 包含系统路径和当前用户的路径
            from sqlalchemy import or_
            query = query.filter(or_(
                LearningPath.is_system == True,
                LearningPath.created_by == request.user_id
            ))
        
        paths = query.order_by(LearningPath.created_at.desc()).all()
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": [path.to_dict() for path in paths]
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/learning_path/paths", methods=["POST"])
@login_required
def create_path():
    """创建学习路径"""
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"code": 400, "message": "路径名称不能为空"}), 400
        
        path = LearningPath(
            name=name,
            description=data.get("description", ""),
            category=data.get("category", "general"),
            is_system=False,
            created_by=request.user_id,
            difficulty=data.get("difficulty", "beginner"),
            estimated_duration=data.get("estimated_duration", 0)
        )
        
        from models.user import db
        db.session.add(path)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "创建成功",
            "data": path.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"创建失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>", methods=["GET"])
@login_required
def get_path(path_id):
    """获取学习路径详情（包含节点）"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        
        # 检查权限：系统路径或创建者
        if not path.is_system and path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权访问此路径"}), 403
        
        path_dict = path.to_dict()
        path_dict["nodes"] = [node.to_dict() for node in path.nodes]
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": path_dict
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>", methods=["PUT"])
@login_required
def update_path(path_id):
    """更新学习路径"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        
        # 检查权限
        if path.is_system:
            return jsonify({"code": 403, "message": "系统路径不可修改"}), 403
        if path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权修改此路径"}), 403
        
        data = request.get_json()
        if "name" in data:
            path.name = data["name"].strip()
        if "description" in data:
            path.description = data.get("description", "")
        if "category" in data:
            path.category = data["category"]
        if "difficulty" in data:
            path.difficulty = data["difficulty"]
        if "estimated_duration" in data:
            path.estimated_duration = data["estimated_duration"]
        
        from models.user import db
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "更新成功",
            "data": path.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>", methods=["DELETE"])
@login_required
def delete_path(path_id):
    """删除学习路径"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        
        # 检查权限
        if path.is_system:
            return jsonify({"code": 403, "message": "系统路径不可删除"}), 403
        if path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权删除此路径"}), 403
        
        from models.user import db
        db.session.delete(path)
        db.session.commit()
        
        return jsonify({"code": 200, "message": "删除成功"})
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>/nodes", methods=["POST"])
@login_required
def add_path_node(path_id):
    """向学习路径添加节点"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        
        # 检查权限
        if path.is_system:
            return jsonify({"code": 403, "message": "系统路径不可修改"}), 403
        if path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权修改此路径"}), 403
        
        data = request.get_json()
        node = LearningPathNode(
            path_id=path_id,
            knowledge_node_id=data.get("knowledge_node_id"),
            node_name=data.get("node_name", "").strip(),
            node_type=data.get("node_type", "knowledge"),
            description=data.get("description", ""),
            order=data.get("order", len(path.nodes)),
            prerequisites=json.dumps(data.get("prerequisites", [])),
            estimated_time=data.get("estimated_time", 0),
            resources=json.dumps(data.get("resources", []))
        )
        
        from models.user import db
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "添加成功",
            "data": node.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"添加失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>/nodes/<int:node_id>", methods=["PUT"])
@login_required
def update_path_node(path_id, node_id):
    """更新学习路径节点"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        node = LearningPathNode.query.get_or_404(node_id)
        
        if node.path_id != path_id:
            return jsonify({"code": 400, "message": "节点不属于此路径"}), 400
        
        # 检查权限
        if path.is_system:
            return jsonify({"code": 403, "message": "系统路径不可修改"}), 403
        if path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权修改此路径"}), 403
        
        data = request.get_json()
        if "node_name" in data:
            node.node_name = data["node_name"].strip()
        if "knowledge_node_id" in data:
            node.knowledge_node_id = data["knowledge_node_id"]
        if "node_type" in data:
            node.node_type = data["node_type"]
        if "description" in data:
            node.description = data["description"]
        if "order" in data:
            node.order = data["order"]
        if "prerequisites" in data:
            node.prerequisites = json.dumps(data["prerequisites"])
        if "estimated_time" in data:
            node.estimated_time = data["estimated_time"]
        if "resources" in data:
            node.resources = json.dumps(data["resources"])
        
        from models.user import db
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "更新成功",
            "data": node.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@bp.route("/learning_path/paths/<int:path_id>/nodes/<int:node_id>", methods=["DELETE"])
@login_required
def delete_path_node(path_id, node_id):
    """删除学习路径节点"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        node = LearningPathNode.query.get_or_404(node_id)
        
        if node.path_id != path_id:
            return jsonify({"code": 400, "message": "节点不属于此路径"}), 400
        
        # 检查权限
        if path.is_system:
            return jsonify({"code": 403, "message": "系统路径不可修改"}), 403
        if path.created_by != request.user_id:
            return jsonify({"code": 403, "message": "无权修改此路径"}), 403
        
        from models.user import db
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({"code": 200, "message": "删除成功"})
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500


@bp.route("/learning_path/user/paths", methods=["GET"])
@login_required
def get_user_paths():
    """获取用户的学习路径实例"""
    try:
        status = request.args.get("status", "")
        
        query = UserLearningPath.query.filter_by(user_id=request.user_id)
        if status:
            query = query.filter_by(status=status)
        
        user_paths = query.order_by(UserLearningPath.updated_at.desc()).all()
        
        result = []
        for up in user_paths:
            up_dict = up.to_dict()
            # 获取进度详情
            progress_records = UserLearningProgress.query.filter_by(
                user_path_id=up.id
            ).all()
            up_dict["progress_details"] = [pr.to_dict() for pr in progress_records]
            result.append(up_dict)
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": result
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/learning_path/user/paths", methods=["POST"])
@login_required
def start_path():
    """开始一个学习路径"""
    try:
        data = request.get_json()
        path_id = data.get("path_id")
        if not path_id:
            return jsonify({"code": 400, "message": "路径ID不能为空"}), 400
        
        path = LearningPath.query.get_or_404(path_id)
        
        # 检查是否已经存在
        existing = UserLearningPath.query.filter_by(
            user_id=request.user_id,
            path_id=path_id,
            status="in_progress"
        ).first()
        
        if existing:
            return jsonify({
                "code": 200,
                "message": "路径已存在",
                "data": existing.to_dict()
            })
        
        user_path = UserLearningPath(
            user_id=request.user_id,
            path_id=path_id,
            status="in_progress",
            progress=0.0
        )
        
        from models.user import db
        db.session.add(user_path)
        db.session.commit()
        
        # 初始化进度记录
        for path_node in path.nodes:
            progress = UserLearningProgress(
                user_id=request.user_id,
                user_path_id=user_path.id,
                path_node_id=path_node.id,
                status="not_started"
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "开始学习成功",
            "data": user_path.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"开始学习失败: {str(e)}"}), 500


@bp.route("/learning_path/user/paths/<int:user_path_id>", methods=["GET"])
@login_required
def get_user_path_detail(user_path_id):
    """获取用户学习路径详情"""
    try:
        user_path = UserLearningPath.query.get_or_404(user_path_id)
        
        if user_path.user_id != request.user_id:
            return jsonify({"code": 403, "message": "无权访问"}), 403
        
        path_dict = user_path.to_dict()
        path_dict["path"]["nodes"] = [node.to_dict() for node in user_path.path.nodes]
        
        # 获取每个节点的进度
        progress_records = UserLearningProgress.query.filter_by(
            user_path_id=user_path_id
        ).all()
        
        progress_map = {pr.path_node_id: pr.to_dict() for pr in progress_records}
        for node in path_dict["path"]["nodes"]:
            node["progress"] = progress_map.get(node["id"], None)
        
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": path_dict
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取失败: {str(e)}"}), 500


@bp.route("/learning_path/user/paths/<int:user_path_id>/progress", methods=["PUT"])
@login_required
def update_progress(user_path_id):
    """更新学习进度"""
    try:
        user_path = UserLearningPath.query.get_or_404(user_path_id)
        
        if user_path.user_id != request.user_id:
            return jsonify({"code": 403, "message": "无权访问"}), 403
        
        data = request.get_json()
        path_node_id = data.get("path_node_id")
        status = data.get("status")
        completion_percentage = data.get("completion_percentage", 0)
        time_spent = data.get("time_spent", 0)
        notes = data.get("notes", "")
        
        if not path_node_id:
            return jsonify({"code": 400, "message": "节点ID不能为空"}), 400
        
        progress = UserLearningProgress.query.filter_by(
            user_path_id=user_path_id,
            path_node_id=path_node_id
        ).first()
        
        if not progress:
            progress = UserLearningProgress(
                user_id=request.user_id,
                user_path_id=user_path_id,
                path_node_id=path_node_id,
                status=status or "in_progress"
            )
            from models.user import db
            db.session.add(progress)
        
        if status:
            progress.status = status
            if status == "in_progress" and not progress.started_at:
                progress.started_at = datetime.utcnow()
            elif status == "completed":
                progress.completed_at = datetime.utcnow()
                progress.completion_percentage = 100.0
        
        if completion_percentage is not None:
            progress.completion_percentage = min(100.0, max(0.0, float(completion_percentage)))
        
        if time_spent is not None:
            progress.time_spent = int(time_spent)
        
        if notes is not None:
            progress.notes = notes
        
        # 更新用户路径总进度
        from models.user import db
        total_nodes = len(user_path.path.nodes)
        completed_nodes = UserLearningProgress.query.filter_by(
            user_path_id=user_path_id,
            status="completed"
        ).count()
        
        user_path.progress = (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0.0
        
        if user_path.progress >= 100.0:
            user_path.status = "completed"
            user_path.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "更新成功",
            "data": progress.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@bp.route("/learning_path/generate", methods=["POST"])
@login_required
def generate_path():
    """基于知识图谱动态生成学习路径"""
    try:
        data = request.get_json()
        target_knowledge = data.get("target_knowledge", [])  # 目标知识点ID列表
        difficulty = data.get("difficulty", "beginner")
        max_nodes = data.get("max_nodes", 10)
        
        # 从Neo4j获取知识图谱数据
        from neo4j_client import driver
        
        # 构建查询：找到目标知识点及其前置依赖
        cypher = """
        MATCH (n)
        WHERE n.id IN $target_ids
        OPTIONAL MATCH (n)<-[:PREREQUISITE|DEPENDS_ON*]-(prereq)
        RETURN DISTINCT n, collect(DISTINCT prereq) as prerequisites
        LIMIT $limit
        """
        
        target_ids = [str(tid) for tid in target_knowledge]
        
        nodes_map = {}
        edges_list = []
        
        with driver.session() as session:
            result = session.run(cypher, target_ids=target_ids, limit=max_nodes * 2)
            
            for record in result:
                n = record["n"]
                if n:
                    node_id = str(n.get("id") or n.id)
                    nodes_map[node_id] = {
                        "id": node_id,
                        "label": n.get("name", ""),
                        "type": list(n.labels)[0] if n.labels else "Node",
                        "properties": dict(n)
                    }
                
                prereqs = record["prerequisites"]
                for prereq in prereqs:
                    if prereq:
                        prereq_id = str(prereq.get("id") or prereq.id)
                        nodes_map[prereq_id] = {
                            "id": prereq_id,
                            "label": prereq.get("name", ""),
                            "type": list(prereq.labels)[0] if prereq.labels else "Node",
                            "properties": dict(prereq)
                        }
                        edges_list.append({
                            "source": prereq_id,
                            "target": node_id,
                            "type": "PREREQUISITE"
                        })
        
        # 使用拓扑排序生成学习顺序
        def topological_sort(nodes, edges):
            """拓扑排序，确定学习顺序"""
            in_degree = {node_id: 0 for node_id in nodes.keys()}
            graph = {node_id: [] for node_id in nodes.keys()}
            
            for edge in edges:
                if edge["source"] in graph and edge["target"] in graph:
                    graph[edge["source"]].append(edge["target"])
                    in_degree[edge["target"]] += 1
            
            queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
            result = []
            
            while queue:
                node_id = queue.pop(0)
                result.append(node_id)
                
                for neighbor in graph[node_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            return result
        
        sorted_nodes = topological_sort(nodes_map, edges_list)
        
        # 创建学习路径节点
        path_nodes = []
        for idx, node_id in enumerate(sorted_nodes[:max_nodes]):
            node_data = nodes_map[node_id]
            path_nodes.append({
                "node_name": node_data["label"],
                "knowledge_node_id": None,  # 可以后续关联到MySQL的KnowledgeNode
                "order": idx + 1,
                "node_type": "knowledge",
                "description": node_data["properties"].get("description", ""),
                "prerequisites": [],
                "estimated_time": 60  # 默认60分钟
            })
        
        return jsonify({
            "code": 200,
            "message": "生成成功",
            "data": {
                "nodes": path_nodes,
                "total_nodes": len(path_nodes),
                "estimated_duration": len(path_nodes) * 60  # 分钟
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"生成失败: {str(e)}"}), 500


@bp.route("/learning_path/user/paths/<int:user_path_id>/adjust", methods=["POST"])
@login_required
def adjust_path(user_path_id):
    """调整学习路径（跳过节点、调整顺序等）"""
    try:
        user_path = UserLearningPath.query.get_or_404(user_path_id)
        
        if user_path.user_id != request.user_id:
            return jsonify({"code": 403, "message": "无权访问"}), 403
        
        data = request.get_json()
        adjustments = data.get("adjustments", {})
        
        # 保存调整信息
        current_adjustments = json.loads(user_path.custom_adjustments) if user_path.custom_adjustments else {}
        current_adjustments.update(adjustments)
        user_path.custom_adjustments = json.dumps(current_adjustments)
        
        # 处理跳过节点
        if "skipped_nodes" in adjustments:
            skipped = adjustments["skipped_nodes"]
            for node_id in skipped:
                progress = UserLearningProgress.query.filter_by(
                    user_path_id=user_path_id,
                    path_node_id=node_id
                ).first()
                if progress:
                    progress.status = "skipped"
        
        # 处理节点顺序调整
        if "node_order" in adjustments:
            # 这里可以更新节点的order，但为了不影响原始路径，我们只保存调整信息
            pass
        
        from models.user import db
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "调整成功",
            "data": user_path.to_dict()
        })
    except Exception as e:
        from models.user import db
        db.session.rollback()
        return jsonify({"code": 500, "message": f"调整失败: {str(e)}"}), 500
