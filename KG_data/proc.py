import json
from neo4j import GraphDatabase
import os

class LiteATTACKImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=100)
    
    def load_core_data(self, file_path):
        """只导入核心数据：技术、战术、技术-战术关系"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with self.driver.session() as session:
            # 只导入技术和技术关系
            techniques = [obj for obj in data['objects'] 
                         if obj.get('type') == 'attack-pattern']
            
            # 批量导入技术节点
            batch_size = 50
            for i in range(0, len(techniques), batch_size):
                batch = techniques[i:i+batch_size]
                self._create_techniques_batch(session, batch)
            
            # 导入战术
            tactics = [obj for obj in data['objects'] 
                      if obj.get('type') == 'x-mitre-tactic']
            for tactic in tactics:
                self._create_tactic(session, tactic)
            
            # 创建技术-战术关系
            self._create_tactic_technique_relations(session, techniques, tactics)
    
    def _create_techniques_batch(self, session, techniques):
        """批量创建技术节点（减少内存占用）"""
        query = """
        UNWIND $techniques as tech
        CREATE (t:Technique {
            id: tech.id,
            name: tech.name,
            description: CASE WHEN size(tech.description) > 500 
                           THEN substring(tech.description, 0, 500) + '...'
                           ELSE tech.description END,
            external_id: CASE WHEN size(tech.external_references) > 0 
                            THEN tech.external_references[0].external_id
                            ELSE '' END
        })
        """
        
        # 预处理数据，只保留必要字段
        tech_data = []
        for tech in techniques:
            tech_data.append({
                'id': tech['id'],
                'name': tech['name'],
                'description': tech.get('description', '')[:500],  # 截断长描述
                'external_references': tech.get('external_references', [])
            })
        
        session.run(query, techniques=tech_data)
    
    def _create_tactic(self, session, tactic):
        """创建战术节点"""
        external_id = ''
        if tactic.get('external_references'):
            external_id = tactic['external_references'][0].get('external_id', '')
        
        query = """
        CREATE (ta:Tactic {
            id: $id,
            name: $name,
            external_id: $external_id,
            shortname: $shortname
        })
        """
        
        session.run(query,
            id=tactic['id'],
            name=tactic['name'],
            external_id=external_id,
            shortname=tactic.get('x_mitre_shortname', '')
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

# 使用
importer = LiteATTACKImporter("bolt://localhost:7687", "neo4j", "K988464noNeo4j")
importer.load_core_data("./cti/enterprise-attack/enterprise-attack.json")