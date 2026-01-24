from flask import Blueprint, jsonify, request
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


@bp.route("/graph/node_types", methods=["GET"])
def get_node_types():
    """
    获取所有节点类型（标签）和边类型
    用于前端动态生成颜色映射
    """
    try:
        with driver.session() as session:
            # 获取所有节点标签
            node_types_query = """
            CALL db.labels()
            YIELD label
            RETURN collect(label) as labels
            """
            node_result = session.run(node_types_query)
            node_labels = []
            for record in node_result:
                labels = record.get("labels", [])
                if labels:
                    node_labels = labels
                    break
            
            # 如果没有获取到,尝试另一种方法
            if not node_labels:
                alt_query = """
                MATCH (n)
                RETURN DISTINCT labels(n) as labels
                LIMIT 100
                """
                alt_result = session.run(alt_query)
                all_labels = set()
                for record in alt_result:
                    labels = record.get("labels", [])
                    all_labels.update(labels)
                node_labels = list(all_labels)
            
            # 获取所有关系类型
            edge_types_query = """
            CALL db.relationshipTypes()
            YIELD relationshipType
            RETURN collect(relationshipType) as types
            """
            edge_result = session.run(edge_types_query)
            edge_types = []
            for record in edge_result:
                types = record.get("types", [])
                if types:
                    edge_types = types
                    break
            
            # 如果没有获取到,尝试另一种方法
            if not edge_types:
                alt_edge_query = """
                MATCH ()-[r]->()
                RETURN DISTINCT type(r) as relType
                LIMIT 100
                """
                alt_edge_result = session.run(alt_edge_query)
                all_edge_types = set()
                for record in alt_edge_result:
                    rel_type = record.get("relType")
                    if rel_type:
                        all_edge_types.add(rel_type)
                edge_types = list(all_edge_types)
            
            return jsonify({
                "code": 200,
                "node_types": node_labels,
                "edge_types": edge_types
            })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"获取类型失败: {str(e)}"
        }), 500


@bp.route("/graph/update_node/<node_id>", methods=["PUT"])
def update_node(node_id):
    """
    更新Neo4j中的节点
    支持更新节点的属性、标签等
    """
    try:
        data = request.json or {}
        
        with driver.session() as session:
            # 构建更新查询
            # 首先找到节点
            find_query = """
            MATCH (n)
            WHERE n.id = $node_id OR toString(id(n)) = $node_id
            RETURN n, labels(n) as labels
            LIMIT 1
            """
            result = session.run(find_query, {"node_id": str(node_id)})
            record = result.single()
            
            if not record:
                return jsonify({
                    "code": 404,
                    "message": "节点不存在"
                }), 404
            
            node = record["n"]
            current_labels = record["labels"]
            
            # 更新属性
            if "properties" in data:
                properties = data["properties"]
                set_props = []
                params = {"node_id": node_id}
                
                for key, value in properties.items():
                    if key not in ["id", "x", "y"]:  # 保留这些特殊属性
                        param_key = f"prop_{key}"
                        set_props.append(f"n.{key} = ${param_key}")
                        params[param_key] = value
                
                if set_props:
                    update_query = f"""
                    MATCH (n)
                    WHERE n.id = $node_id OR toString(id(n)) = $node_id
                    SET {', '.join(set_props)}
                    RETURN n
                    """
                    params["node_id"] = str(node_id)
                    session.run(update_query, params)
            
            # 更新标签（如果提供了新标签）
            if "type" in data:
                new_label = data["type"]
                if new_label and new_label not in current_labels:
                    # 移除所有旧标签
                    for old_label in current_labels:
                        # 使用字符串格式化来动态设置标签
                        remove_old = f"""
                        MATCH (n)
                        WHERE n.id = $node_id OR toString(id(n)) = $node_id
                        REMOVE n:`{old_label}`
                        RETURN n
                        """
                        session.run(remove_old, {"node_id": str(node_id)})
                    
                    # 添加新标签
                    add_new = f"""
                    MATCH (n)
                    WHERE n.id = $node_id OR toString(id(n)) = $node_id
                    SET n:`{new_label}`
                    RETURN n
                    """
                    session.run(add_new, {"node_id": str(node_id)})
            
            # 更新label（显示名称）
            if "label" in data or "name" in data:
                name = data.get("label") or data.get("name")
                update_name_query = """
                MATCH (n)
                WHERE n.id = $node_id OR toString(id(n)) = $node_id
                SET n.name = $name
                RETURN n
                """
                session.run(update_name_query, {"node_id": str(node_id), "name": name})
            
            return jsonify({
                "code": 200,
                "message": "节点更新成功"
            })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"更新节点失败: {str(e)}"
        }), 500


@bp.route("/graph/delete_node/<node_id>", methods=["DELETE"])
def delete_node(node_id):
    """
    删除Neo4j中的节点及其所有关系
    """
    try:
        with driver.session() as session:
            # 先检查节点是否存在
            check_query = """
            MATCH (n)
            WHERE n.id = $node_id OR toString(id(n)) = $node_id
            RETURN n
            LIMIT 1
            """
            result = session.run(check_query, {"node_id": str(node_id)})
            if not result.single():
                return jsonify({
                    "code": 404,
                    "message": "节点不存在"
                }), 404
            
            # 删除节点及其所有关系
            delete_query = """
            MATCH (n)
            WHERE n.id = $node_id OR toString(id(n)) = $node_id
            DETACH DELETE n
            RETURN count(n) as deleted
            """
            result = session.run(delete_query, {"node_id": str(node_id)})
            
            return jsonify({
                "code": 200,
                "message": "节点删除成功"
            })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"删除节点失败: {str(e)}"
        }), 500


@bp.route("/graph/property_config", methods=["GET"])
def get_property_config():
    """
    获取属性显示配置
    支持不同数据源的知识图谱配置不同的属性显示方式
    """
    # 从查询参数获取数据源类型，默认为 'default'
    data_source = request.args.get("data_source", "default")
    
    # 预定义的属性配置
    # 可以根据不同的数据源返回不同的配置
    configs = {
        "default": {
            "groups": [
                {
                    "name": "基本信息",
                    "order": 1,
                    "properties": ["name", "label", "id", "type", "description"]
                },
                {
                    "name": "扩展信息",
                    "order": 2,
                    "properties": []  # 空数组表示显示所有其他属性
                }
            ],
            "property_labels": {
                "name": "名称",
                "label": "标签",
                "id": "ID",
                "type": "类型",
                "description": "描述"
            },
            "hidden_properties": ["x", "y"],  # 隐藏的属性
            "property_order": []  # 空数组表示使用默认顺序
        },
        "attack": {
            "groups": [
                {
                    "name": "基本信息",
                    "order": 1,
                    "properties": ["name", "external_id", "type", "description"]
                },
                {
                    "name": "其他信息",
                    "order": 3,
                    "properties": ["platform", "detection", "created", "modified", "version"]
                },
                {
                    "name": "扩展属性",
                    "order": 4,
                    "properties": []
                }
            ],
            "property_labels": {
                "name": "名称",
                "external_id": "外部ID",
                "type": "类型",
                "description": "描述",
                "x_mitre_platforms": "MITRE平台",
                "x_mitre_permissions_required": "所需权限",
                "x_mitre_data_sources": "数据源",
                "x_mitre_defense_bypassed": "绕过防御",
                "kill_chain_phases": "杀伤链阶段",
                "platform": "平台",
                "detection": "检测",
                "created": "创建时间",
                "modified": "修改时间",
                "version": "版本"
            },
            "hidden_properties": ["x", "y", "id"],
            "property_order": []
        }
    }
    
    # 返回对应数据源的配置，如果没有则返回默认配置
    config = configs.get(data_source, configs["default"])
    
    return jsonify({
        "code": 200,
        "data_source": data_source,
        "config": config
    })


@bp.route("/graph/property_config", methods=["POST"])
def save_property_config():
    """
    保存属性显示配置（管理员功能）
    允许管理员自定义不同数据源的属性显示配置
    """
    try:
        data = request.json or {}
        data_source = data.get("data_source", "default")
        config = data.get("config", {})
        
        # 这里可以将配置保存到数据库或配置文件
        # 目前先返回成功，实际项目中可以保存到数据库
        
        return jsonify({
            "code": 200,
            "message": "配置保存成功",
            "data_source": data_source
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"保存配置失败: {str(e)}"
        }), 500
