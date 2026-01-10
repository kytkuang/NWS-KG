from functools import wraps

from flask import Blueprint, jsonify, request

from models import db, User, KnowledgeNode, KnowledgeRelation
from utils.security import verify_token

bp = Blueprint("knowledge", __name__)


def admin_required(f):
  """
  简单的管理员权限校验：
  - 从 Authorization: Bearer <token> 中解析出 user_id
  - 查询用户并检查 is_admin 标记
  """

  @wraps(f)
  def wrapper(*args, **kwargs):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
      return jsonify({"success": False, "message": "未提供认证令牌"}), 401

    token = auth_header.split(" ")[1]
    try:
      payload = verify_token(token)
    except Exception as e:
      return jsonify({"success": False, "message": str(e)}), 401

    user = User.query.get(payload.get("user_id"))
    if not user or not user.is_admin:
      return jsonify({"success": False, "message": "无权限执行此操作"}), 403

    # 将当前用户放入 request 上下文，必要时可使用
    request.current_user = user
    return f(*args, **kwargs)

  return wrapper


@bp.route("/knowledge/nodes", methods=["GET"])
def list_nodes():
  """
  分页查询知识点（任何登录用户可用，前端用于知识管理页面和学习辅助）
  支持简单搜索：?q=SQL&category=technique&page=1&page_size=20
  """
  q = request.args.get("q", "").strip()
  category = request.args.get("category", "").strip()
  page = int(request.args.get("page", 1))
  page_size = int(request.args.get("page_size", 20))
  page = max(page, 1)
  page_size = max(min(page_size, 100), 1)

  query = KnowledgeNode.query
  if q:
    query = query.filter(KnowledgeNode.name.like(f"%{q}%"))
  if category:
    query = query.filter_by(category=category)

  total = query.count()
  items = (
      query.order_by(KnowledgeNode.created_at.desc())
      .offset((page - 1) * page_size)
      .limit(page_size)
      .all()
  )

  return jsonify(
      {
          "success": True,
          "total": total,
          "page": page,
          "page_size": page_size,
          "items": [n.to_dict() for n in items],
      }
  )


@bp.route("/knowledge/nodes", methods=["POST"])
@admin_required
def create_node():
  """创建知识点（管理员）"""
  data = request.json or {}
  name = (data.get("name") or "").strip()
  if not name:
    return jsonify({"success": False, "message": "知识点名称不能为空"}), 400

  node = KnowledgeNode(
      name=name,
      category=(data.get("category") or "concept").strip(),
      description=data.get("description") or "",
      source=(data.get("source") or "custom").strip(),
      neo4j_id=(data.get("neo4j_id") or "").strip() or None,
  )
  db.session.add(node)
  db.session.commit()
  return jsonify({"success": True, "item": node.to_dict()})


@bp.route("/knowledge/nodes/<int:node_id>", methods=["PUT"])
@admin_required
def update_node(node_id: int):
  """更新知识点信息（管理员）"""
  node = KnowledgeNode.query.get_or_404(node_id)
  data = request.json or {}

  if "name" in data:
    name = (data.get("name") or "").strip()
    if not name:
      return jsonify({"success": False, "message": "知识点名称不能为空"}), 400
    node.name = name

  if "category" in data:
    node.category = (data.get("category") or node.category).strip()
  if "description" in data:
    node.description = data.get("description") or ""
  if "source" in data:
    node.source = (data.get("source") or node.source).strip()
  if "neo4j_id" in data:
    node.neo4j_id = (data.get("neo4j_id") or "").strip() or None

  db.session.commit()
  return jsonify({"success": True, "item": node.to_dict()})


@bp.route("/knowledge/nodes/<int:node_id>", methods=["DELETE"])
@admin_required
def delete_node(node_id: int):
  """删除知识点（管理员）"""
  node = KnowledgeNode.query.get_or_404(node_id)

  # 同步删除相关关系
  KnowledgeRelation.query.filter(
      (KnowledgeRelation.source_id == node.id)
      | (KnowledgeRelation.target_id == node.id)
  ).delete(synchronize_session=False)

  db.session.delete(node)
  db.session.commit()
  return jsonify({"success": True})


@bp.route("/knowledge/relations", methods=["POST"])
@admin_required
def create_relation():
  """创建知识点之间的关系（管理员）"""
  data = request.json or {}
  try:
    source_id = int(data.get("source_id"))
    target_id = int(data.get("target_id"))
  except (TypeError, ValueError):
    return jsonify({"success": False, "message": "source_id / target_id 无效"}), 400

  if source_id == target_id:
    return jsonify({"success": False, "message": "不能创建指向自己的关系"}), 400

  # 确认两端节点存在
  source = KnowledgeNode.query.get_or_404(source_id)
  target = KnowledgeNode.query.get_or_404(target_id)

  relation = KnowledgeRelation(
      source_id=source.id,
      target_id=target.id,
      relation_type=(data.get("relation_type") or "related").strip(),
      description=data.get("description") or "",
  )
  db.session.add(relation)
  db.session.commit()
  return jsonify({"success": True, "item": relation.to_dict()})


@bp.route("/knowledge/relations/<int:rel_id>", methods=["DELETE"])
@admin_required
def delete_relation(rel_id: int):
  """删除关系（管理员）"""
  rel = KnowledgeRelation.query.get_or_404(rel_id)
  db.session.delete(rel)
  db.session.commit()
  return jsonify({"success": True})


@bp.route("/knowledge/relations/by-node/<int:node_id>", methods=["GET"])
def list_relations_by_node(node_id: int):
  """
  查看某个知识点相关的所有关系
  （学习辅助和管理界面都可以使用）
  """
  node = KnowledgeNode.query.get_or_404(node_id)
  out_rels = KnowledgeRelation.query.filter_by(source_id=node.id).all()
  in_rels = KnowledgeRelation.query.filter_by(target_id=node.id).all()

  return jsonify(
      {
          "success": True,
          "node": node.to_dict(),
          "out_relations": [r.to_dict() for r in out_rels],
          "in_relations": [r.to_dict() for r in in_rels],
      }
  )


@bp.route("/knowledge/graph/subgraph", methods=["GET"])
def get_knowledge_subgraph():
  """
  返回基于 KnowledgeNode / KnowledgeRelation 的一个小子图，
  给前端做管理界面中的可视化编辑。

  - 如果提供 center_id，则取该节点和与之直接相连的关系
  - 否则返回最近创建的前 N 个节点及其关系
  """
  center_id = request.args.get("center_id", type=int)
  limit = request.args.get("limit", default=50, type=int)
  limit = max(min(limit, 200), 10)

  nodes = {}
  edges = []

  if center_id:
    center = KnowledgeNode.query.get_or_404(center_id)
    rels = KnowledgeRelation.query.filter(
        (KnowledgeRelation.source_id == center.id)
        | (KnowledgeRelation.target_id == center.id)
    ).all()

    nodes[str(center.id)] = center.to_dict()
    for r in rels:
      s = KnowledgeNode.query.get(r.source_id)
      t = KnowledgeNode.query.get(r.target_id)
      if s:
        nodes[str(s.id)] = s.to_dict()
      if t:
        nodes[str(t.id)] = t.to_dict()
      edges.append(
          {
              "id": r.id,
              "source": str(r.source_id),
              "target": str(r.target_id),
              "type": r.relation_type,
          }
      )
  else:
    # 默认返回最近创建的节点及其相互关系
    base_nodes = (
        KnowledgeNode.query.order_by(KnowledgeNode.created_at.desc())
        .limit(limit)
        .all()
    )
    for n in base_nodes:
      nodes[str(n.id)] = n.to_dict()

    rels = KnowledgeRelation.query.filter(
        KnowledgeRelation.source_id.in_([n.id for n in base_nodes])
        | KnowledgeRelation.target_id.in_([n.id for n in base_nodes])
    ).all()
    for r in rels:
      edges.append(
          {
              "id": r.id,
              "source": str(r.source_id),
              "target": str(r.target_id),
              "type": r.relation_type,
          }
      )

  return jsonify(
      {
          "success": True,
          "nodes": list(nodes.values()),
          "edges": edges,
      }
  )

