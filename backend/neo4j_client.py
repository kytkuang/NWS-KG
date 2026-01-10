from neo4j import GraphDatabase
import config.neo4j_config as cfg

driver = GraphDatabase.driver(
    cfg.NEO4J_URI,
    auth=(cfg.NEO4J_USER, cfg.NEO4J_PASSWORD)
)

def query(cypher, params=None):
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [r.data() for r in result]
