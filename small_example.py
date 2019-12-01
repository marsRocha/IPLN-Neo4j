#!/usr/bin/env python3
from neo4j import GraphDatabase #import of neo4j

def createNode(driver, t, name):
    with driver.session() as session:
        session.run("CREATE (node:"+t+" {name: $name}) RETURN node.name",t = t, name = name)
            
def createRelation(driver, n1, n2, r):
    with driver.session() as session:
        session.run("MATCH (node1:Warehouse {name: $n1}),(node2:Store {name: $n2}) MERGE (node1)-[r:"+r+"]->(node2) RETURN node1.name,type(r),node2.name",n1=n1,n2=n2,r=r)

def main():
    driver = GraphDatabase.driver(uri="bolt://localhost:7687" , auth=("neo4j", "eheh"))
    
    createNode(driver,"Store","Lewis")
    createNode(driver,"Warehouse","Clothing")
    createRelation(driver,"Clothing","Lewis","Provides")

if __name__ == "__main__":
    main()