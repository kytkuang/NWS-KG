from flask import Blueprint, jsonify
from neo4j_client import driver

bp = Blueprint("graph", __name__)


@bp.route("/graph/get_subgraph", methods=["GET"])
def get_subgraph():
    """
    从 Neo4j 中取一小部分子图，并整理成前端易用的 nodes / edges 结构
    严格保证：session 内消费 result，避免 Result has been consumed 错误
    """
    cypher = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    LIMIT 200
    """

    nodes = {}
    edges = []

    try:
        with driver.session() as session:
            result = session.run(cypher)

            for idx, record in enumerate(result):
                n = record["n"]
                m = record["m"]
                r = record["r"]

                # 节点 ID：优先业务 ID，否则 Neo4j 内部 ID
                n_id = str(n.get("id") or n.id)
                m_id = str(m.get("id") or m.id)

                # 源节点
                if n_id not in nodes:
                    nodes[n_id] = {
                        "id": n_id,
                        "label": n.get("name", ""),
                        "type": list(n.labels)[0] if n.labels else "Node",
                        "x": n.get("x"),
                        "y": n.get("y"),
                        "properties": dict(n)
                    }

                # 目标节点
                if m_id not in nodes:
                    nodes[m_id] = {
                        "id": m_id,
                        "label": m.get("name", ""),
                        "type": list(m.labels)[0] if m.labels else "Node",
                        "x": m.get("x"),
                        "y": m.get("y"),
                        "properties": dict(m)
                    }

                # 边
                edges.append({
                    "id": f"{n_id}_{r.type}_{m_id}_{idx}",
                    "source": n_id,
                    "target": m_id,
                    "type": r.type,
                    "label": r.type
                })

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"数据库查询失败: {str(e)}"
        }), 500

    return jsonify({
        "code": 200,
        "nodes": list(nodes.values()),
        "edges": edges
    })


@bp.route("/graph/attack_data", methods=["GET"])
def get_attack_data():
    """
    获取 ATT&CK 框架数据（Technique / Tactic / Subtechnique / Mitigation / Group / Software）
    返回完整节点属性，保证前后端一致
    """
    cypher = """
    MATCH (n)-[r]->(m)
    WHERE n:Technique OR n:Tactic OR n:Subtechnique
       OR n:Mitigation OR n:Group OR n:Software
    RETURN n, r, m
    LIMIT 200
    """

    nodes = {}
    edges = []

    try:
        with driver.session() as session:
            result = session.run(cypher)

            for idx, record in enumerate(result):
                n = record["n"]
                m = record["m"]
                r = record["r"]

                n_id = str(n.get("id") or n.id)
                m_id = str(m.get("id") or m.id)

                # 源节点
                if n_id not in nodes:
                    nodes[n_id] = {
                        "id": n_id,
                        "display_id": str(n.get("external_id") or n.get("id") or n_id),
                        "label": n.get("name", ""),
                        "type": list(n.labels)[0] if n.labels else "Node",
                        "external_id": n.get("external_id"),
                        "description": n.get("description"),
                        "platform": n.get("platform"),
                        "detection": n.get("detection"),
                        "created": n.get("created"),
                        "modified": n.get("modified"),
                        "version": n.get("version"),
                        "x_mitre_platforms": n.get("x_mitre_platforms"),
                        "x_mitre_permissions_required": n.get("x_mitre_permissions_required"),
                        "x_mitre_data_sources": n.get("x_mitre_data_sources"),
                        "x_mitre_defense_bypassed": n.get("x_mitre_defense_bypassed"),
                        "kill_chain_phases": n.get("kill_chain_phases"),
                        "x": n.get("x"),
                        "y": n.get("y"),
                        "properties": dict(n)
                    }

                # 目标节点
                if m_id not in nodes:
                    nodes[m_id] = {
                        "id": m_id,
                        "display_id": str(m.get("external_id") or m.get("id") or m_id),
                        "label": m.get("name", ""),
                        "type": list(m.labels)[0] if m.labels else "Node",
                        "external_id": m.get("external_id"),
                        "description": m.get("description"),
                        "platform": m.get("platform"),
                        "detection": m.get("detection"),
                        "created": m.get("created"),
                        "modified": m.get("modified"),
                        "version": m.get("version"),
                        "x_mitre_platforms": m.get("x_mitre_platforms"),
                        "x_mitre_permissions_required": m.get("x_mitre_permissions_required"),
                        "x_mitre_data_sources": m.get("x_mitre_data_sources"),
                        "x_mitre_defense_bypassed": m.get("x_mitre_defense_bypassed"),
                        "kill_chain_phases": m.get("kill_chain_phases"),
                        "x": m.get("x"),
                        "y": m.get("y"),
                        "properties": dict(m)
                    }

                # 边
                edges.append({
                    "id": f"{n_id}_{r.type}_{m_id}_{idx}",
                    "source": n_id,
                    "target": m_id,
                    "type": r.type,
                    "label": r.type
                })


    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取 ATT&CK 数据失败: {str(e)}"
        }), 500

    return jsonify({
        "code": 200,
        "nodes": list(nodes.values()),
        "edges": edges,
        "message": "ATT&CK 数据获取成功"
    })
