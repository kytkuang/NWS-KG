from neo4j import GraphDatabase

class ATTACKVerifier:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def verify_import(self):
        """验证导入结果"""
        queries = [
            ("技术数量", "MATCH (t:Technique) RETURN count(t) as count"),
            ("战术数量", "MATCH (t:Tactic) RETURN count(t) as count"),
            ("缓解措施数量", "MATCH (m:Mitigation) RETURN count(m) as count"),
            ("攻击组织数量", "MATCH (g:Group) RETURN count(g) as count"),
            ("软件数量", "MATCH (s:Software) RETURN count(s) as count"),
            ("数据源数量", "MATCH (d:DataSource) RETURN count(d) as count"),
            ("关系总数", "MATCH ()-[r]->() RETURN count(r) as count"),
            ("最常用的技术", """
                MATCH (t:Technique)<-[r:USES]-()
                RETURN t.name, t.external_id, count(r) as usage_count 
                ORDER BY usage_count DESC LIMIT 10
            """),
            ("技术最多的战术", """
                MATCH (ta:Tactic)<-[:BELONGS_TO]-(t:Technique)
                RETURN ta.name, ta.external_id, count(t) as technique_count 
                ORDER BY technique_count DESC
            """)
        ]
        
        with self.driver.session() as session:
            for name, query in queries:
                result = session.run(query)
                for record in result:
                    print(f"{name}: {record['count'] if 'count' in record else record}")
    
    def search_technique(self, search_term):
        """搜索技术"""
        query = """
        MATCH (t:Technique)
        WHERE t.name CONTAINS $search OR t.description CONTAINS $search OR t.external_id CONTAINS $search
        OPTIONAL MATCH (t)-[:BELONGS_TO]->(ta:Tactic)
        RETURN t.external_id, t.name, t.description, collect(ta.name) as tactics
        LIMIT 20
        """
        
        with self.driver.session() as session:
            result = session.run(query, search=search_term)
            for record in result:
                print(f"\n{record['t.external_id']}: {record['t.name']}")
                print(f"所属战术: {', '.join(record['tactics'])}")
                if record['t.description']:
                    print(f"描述: {record['t.description'][:200]}...")
    
    def get_technique_details(self, technique_id):
        """获取技术详情"""
        query = """
        MATCH (t:Technique {external_id: $id})
        OPTIONAL MATCH (t)-[:BELONGS_TO]->(ta:Tactic)
        OPTIONAL MATCH (t)<-[:MITIGATES]-(m:Mitigation)
        OPTIONAL MATCH (t)<-[:USES]-(s:Software)
        OPTIONAL MATCH (t)<-[:USES]-(g:Group)
        OPTIONAL MATCH (t)-[:SUB_TECHNIQUE_OF]->(parent:Technique)
        OPTIONAL MATCH (t)<-[:SUB_TECHNIQUE_OF]-(sub:Technique)
        RETURN 
            t.external_id as external_id,
            t.name as name,
            t.description as description,
            t.platform as platforms,
            t.detection as detection,
            collect(DISTINCT ta.name) as tactics,
            collect(DISTINCT m.name) as mitigations,
            collect(DISTINCT s.name) as software,
            collect(DISTINCT g.name) as groups,
            collect(DISTINCT parent.name) as parent_techniques,
            collect(DISTINCT sub.name) as sub_techniques
        """
        
        with self.driver.session() as session:
            result = session.run(query, id=technique_id)
            for record in result:
                print(f"\n技术ID: {record['external_id']}")
                print(f"名称: {record['name']}")
                print(f"平台: {', '.join(record['platforms'])}")
                print(f"所属战术: {', '.join(record['tactics'])}")
                if record['parent_techniques']:
                    print(f"父技术: {', '.join(record['parent_techniques'])}")
                if record['sub_techniques']:
                    print(f"子技术: {', '.join(record['sub_techniques'])}")
                if record['mitigations']:
                    print(f"缓解措施: {', '.join(record['mitigations'])}")
                if record['software']:
                    print(f"相关软件: {', '.join(record['software'])}")
                if record['groups']:
                    print(f"使用组织: {', '.join(record['groups'])}")
                if record['detection']:
                    print(f"\n检测方法:\n{record['detection']}")

# 使用示例
if __name__ == "__main__":
    verifier = ATTACKVerifier("bolt://localhost:7687", "neo4j", "K988464noNeo4j")
    
    try:
        print("=== 验证导入结果 ===")
        verifier.verify_import()
        
        print("\n=== 搜索技术示例 ===")
        verifier.search_technique("Execution")
        
        print("\n=== 技术详情示例 ===")
        verifier.get_technique_details("T1059")  # Command and Scripting Interpreter
    
    finally:
        verifier.close()