#!/usr/bin/env python3
from neo4j import GraphDatabase #import of neo4j

def main():
    driver = GraphDatabase.driver(uri="bolt://localhost:7687" , auth=("neo4j", "eheh"))
        
    warehouse = "Clothing"
    store = "Lewis"
    relation = "Provides"

    with driver.session() as session:
        result = session.run("CREATE (node1:Warehouse {name: $warehouse})-[r:"+relation+"]->(node2:Store {name: $store}) Return node1",warehouse=warehouse,store=store,relation=relation)
        for record in result:
            n = record["node1"]
            print(n)

if __name__ == "__main__":
    main()