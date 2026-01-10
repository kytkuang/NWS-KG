from flask import Blueprint, jsonify
from neo4j_client import driver

bp = Blueprint("graph", __name__)


@bp.route("/graph/get_subgraph", methods=["GET"])
def get_subgraph():
    """
    从 Neo4j 中取一小部分子图，并整理成前端易用的 nodes / edges 结构
    这里直接使用 Neo4j 的 Node / Relationship 对象，避免被转换成 dict 后缺少 .id / .labels 等属性。
    """
    cypher = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m,
           n.x as n_x, n.y as n_y,
           m.x as m_x, m.y as m_y
    LIMIT 100
    """

    nodes = {}
    edges = []
    record_count = 0

    try:
        with driver.session() as session:
            result = session.run(cypher)
            for record in result:
                record_count += 1
                n = record["n"]  # neo4j.data.Node
                m = record["m"]
                r = record["r"]  # neo4j.data.Relationship

                # 统一用业务属性 id（如果有），否则用内部 id，确保是字符串格式
                n_id = str(n.get("id") or n.id)
                m_id = str(m.get("id") or m.id)

                n_labels = list(n.labels)
                m_labels = list(m.labels)

                # 获取或计算节点坐标
                n_x = record.get("n_x") or n.get("x")
                n_y = record.get("n_y") or n.get("y")
                m_x = record.get("m_x") or m.get("x")
                m_y = record.get("m_y") or m.get("y")

                nodes[str(n_id)] = {
                    "id": str(n_id),
                    "label": n.get("name", ""),
                    "type": n_labels[0] if n_labels else "Node",
                    "x": float(n_x) if n_x is not None else None,
                    "y": float(n_y) if n_y is not None else None,
                }
                nodes[str(m_id)] = {
                    "id": str(m_id),
                    "label": m.get("name", ""),
                    "type": m_labels[0] if m_labels else "Node",
                    "x": float(m_x) if m_x is not None else None,
                    "y": float(m_y) if m_y is not None else None,
                }

                edges.append(
                    {
                        "source": str(n_id),
                        "target": str(m_id),
                        "type": r.type,
                    }
                )

        print(f"查询到 {record_count} 条记录，{len(nodes)} 个节点，{len(edges)} 条边")

    except Exception as e:
        print(f"Neo4j查询错误: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"数据库查询失败: {str(e)}"
        }), 500

    return jsonify(
        {
            "code": 200,
            "nodes": list(nodes.values()),
            "edges": edges,
        }
    )
