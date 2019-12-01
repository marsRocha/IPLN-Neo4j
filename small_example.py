#!/usr/bin/env python3
from neo4j import GraphDatabase #import of neo4j

def main():
    driver = GraphDatabase.driver(uri="bolt://localhost:7687" , auth=("neo4j", "eheh"))
        
    warehouse = "Clothing"
    store = "Lewis"
    relation = "Provides"

    with driver.session() as session:
        session.run("CREATE (node1:Warehouse {name: $warehouse})-[r:"+relation+"]->(node2:Store {name: $store})",warehouse=warehouse,store=store,relation=relation)
        
if __name__ == "__main__":
    main()