#!/usr/bin/env python3

import re
import subprocess
import sys
import fileinput
from py2neo import Graph, Node, Relatioship
#authenticate("localhost:7474","neo4j", "somepassword")
#graph = Graph("http://localhost:7474/db/data/")
#graph.cypher.execute("CREATE(alice:Person {name:'Alice' , age:15})->[:Friendof]->(bob:Person {name: 'Bob' , age:14})")
"""for record in graph.cypher.execute("MATCH(p {title:'The Movie'})RETURN p"):
    if (record[0]==None):
        print "None"
    else:
        print (record[0])
"""

def main():
    file = sys.argv[1]

    #Initiate connection and create session
    graph = Graph(host="bolt://localhost:7687",auth=("neo4j", "eheh"))
    #graph = Graph("http://localhost:7474/db/data/")
    #session = graphdb.session()
