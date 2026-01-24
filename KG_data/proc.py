import json
from neo4j import GraphDatabase
import os

class LiteATTACKImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=100)
    
    def clear_database(self):
        """清空数据库中的所有节点和关系"""
        print("正在清空现有数据库...")
        with self.driver.session() as session:
            # 删除所有节点和关系
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")
    
    def load_core_data(self, file_path):
        """只导入核心数据：技术、战术、技术-战术关系"""
        print(f"开始导入数据文件: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with self.driver.session() as session:
            print("正在处理技术节点...")
            # 只导入技术
            techniques = [obj for obj in data['objects'] 
                         if obj.get('type') == 'attack-pattern']
            
            # 批量导入技术节点
            batch_size = 100
            for i in range(0, len(techniques), batch_size):
                batch = techniques[i:i+batch_size]
                self._create_techniques_batch(session, batch)
                print(f"已导入技术节点: {min(i+batch_size, len(techniques))}/{len(techniques)}")
            
            print("正在处理战术节点...")
            # 导入战术
            tactics = [obj for obj in data['objects'] 
                      if obj.get('type') == 'x-mitre-tactic']
            for tactic in tactics:
                self._create_tactic(session, tactic)
            print(f"已导入战术节点: {len(tactics)}个")
            
            print("正在创建技术-战术关系...")
            # 创建技术-战术关系
            self._create_tactic_technique_relations(session, techniques, tactics)
            print("数据导入完成！")
    
    def _create_techniques_batch(self, session, techniques):
        """批量创建技术节点（去除字数限制）"""
        query = """
        UNWIND $techniques as tech
        CREATE (t:Technique {
            id: tech.id,
            name: tech.name,
            description: tech.description,
            external_id: CASE WHEN size(tech.external_references) > 0 
                            THEN tech.external_references[0].external_id
                            ELSE '' END,
            url: CASE WHEN size(tech.external_references) > 0 
                     THEN tech.external_references[0].url
                     ELSE '' END,
            created: tech.created,
            modified: tech.modified
        })
        """
        
        # 预处理数据，保留完整信息
        tech_data = []
        for tech in techniques:
            description = tech.get('description', '')
            # 不再截断描述
            external_refs = tech.get('external_references', [])
            external_id = ''
            url = ''
            if external_refs:
                external_id = external_refs[0].get('external_id', '')
                url = external_refs[0].get('url', '')
            
            tech_data.append({
                'id': tech['id'],
                'name': tech['name'],
                'description': description,
                'external_references': external_refs,
                'created': tech.get('created', ''),
                'modified': tech.get('modified', '')
            })
        
        session.run(query, techniques=tech_data)
    
    def _create_tactic(self, session, tactic):
        """创建战术节点（去除字数限制）"""
        external_id = ''
        url = ''
        if tactic.get('external_references'):
            external_id = tactic['external_references'][0].get('external_id', '')
            url = tactic['external_references'][0].get('url', '')
        
        query = """
        CREATE (ta:Tactic {
            id: $id,
            name: $name,
            description: $description,
            external_id: $external_id,
            shortname: $shortname,
            url: $url,
            created: $created,
            modified: $modified
        })
        """
        
        session.run(query,
            id=tactic['id'],
            name=tactic['name'],
            description=tactic.get('description', ''),
            external_id=external_id,
            shortname=tactic.get('x_mitre_shortname', ''),
            url=url,
            created=tactic.get('created', ''),
            modified=tactic.get('modified', '')
        )
    
    def _create_tactic_technique_relations(self, session, techniques, tactics):
        """创建技术-战术关系"""
        # 创建战术映射表
        tactic_map = {}
        for tactic in tactics:
            shortname = tactic.get('x_mitre_shortname')
            if shortname:
                tactic_map[shortname] = tactic['id']
        
        # 批量创建关系
        relations = []
        for tech in techniques:
            kill_chain_phases = tech.get('kill_chain_phases', [])
            for phase in kill_chain_phases:
                if phase.get('kill_chain_name') == 'mitre-attack':
                    phase_name = phase.get('phase_name')
                    if phase_name in tactic_map:
                        relations.append({
                            'tech_id': tech['id'],
                            'tactic_id': tactic_map[phase_name]
                        })
        
        # 批量执行
        query = """
        UNWIND $relations as rel
        MATCH (t:Technique {id: rel.tech_id})
        MATCH (ta:Tactic {id: rel.tactic_id})
        CREATE (t)-[:BELONGS_TO]->(ta)
        """
        
        if relations:
            session.run(query, relations=relations)
            print(f"已创建技术-战术关系: {len(relations)}条")

# 使用
importer = LiteATTACKImporter("bolt://localhost:7687", "neo4j", "K988464noNeo4j")

# 1. 先清空数据库
importer.clear_database()

# 2. 重新导入完整数据
importer.load_core_data("./cti/enterprise-attack/enterprise-attack.json")