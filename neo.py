#!/usr/bin/env python3

import re
import subprocess
import sys
import fileinput
from neo4j import GraphDatabase #import of neo4j


def formatText(text):

    listPhrases = []

    #Formats the text by paragraphs and adds them to listParagraphs for later use
    aux = re.sub(r"([.!?]) ", r"\1SeparadorA1IPLN", text)
    listPhrases = aux.split("SeparadorA1IPLN")

    phrases = []

    for phrase in listPhrases:
        phrases.append(phrase)

    return phrases

#neo4j functions
def createNode(session,name, persons):
    node = session.run("CREATE(a:Person{surename:$name}) RETURN a.surename", name = name)
    persons[name]= node

#adds a relatioship to two existing nodes, from person1 to person2
def addRelation(session,person1, person2, relation):
    #verifies if nodes exist, if they do ... do nothing
    session.run("MERGE (p1:Person {surename: $person1}) RETURN p1.surename",person1 = person1)
    session.run("MERGE (p2:Person {surename: $person2}) RETURN p2.surename",person2 = person2)
    #adds relation to nodes
    session.run("MATCH(p1:Person),(p2:Person) WHERE p1.surename = $person1 AND p2.surename = $person2 CREATE (p1)-[:"+relation+"]->(p2)", person1 = person1, person2 = person2)

def getPerson(name, people):
    p = people.get(name)
    return p

def main():
    file = sys.argv[1]

    #Initiate connection and create session
    graphdb = GraphDatabase.driver(uri="bolt://localhost:7687" , auth=("neo4j", "eheh"))
    session = graphdb.session()
    
    text = ""
    # Reads file
    for line in fileinput.input(file):
        text += line

    
    lastPerson = "" 

    phrases = []

    phrases = formatText(text)

    p = []
    pM = r"(?:[A-ZÀ-Ü]\w+|[A-ZÀ-Ü]\.|[A-ZÀ-Ü][a-z]\.)"
    rS = r"(?:casado|casou|divorciado|divorciou|namorado|namorada|esposa|marido)"

    for phrase in phrases:
        #Equitecar nomes e relationStatus
        ph = re.sub(r"(?:o|a|O|A|do|da) " + f"({pM})", r'{\1}:p', phrase)
        ph = re.sub(f" ({rS})", r'{\1}:r', ph)
        p.append(ph)

    for phrase in p:
        if(re.search(r"{(.*?)}:r", phrase)):
            relation = re.findall(r"{(\w+)}:r", phrase)
            if(re.search(r"(.*?):p", phrase)):
                result = re.findall(r"{(\w+)}:p",phrase)
                if(len(result) > 1):
                    
                    addRelation(session, result[0], result[1], relation[0])     
                lastPerson = result[len(result) - 1]    
#print(p)




    nome = "Kermit"
    #createNode(session,nome,nodeperson)
    #addRelation(session,"Tell ",nome,"daddychocked")


if __name__ == "__main__":
    main()