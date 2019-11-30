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
    session.run("MERGE (p1:Person {surename: $person1})",person1 = person1)
    session.run("MERGE (p2:Person {surename: $person2})",person2 = person2)
    #adds relation to nodes
    print(person1+" "+ person2 +" "+ relation)
    session.run("MATCH (p1:Person { surename: $person1 }),(p2:Person { surename: $person2 }) MERGE (p1)-[r:"+relation +"]->(p2) RETURN p1.surename, type(r), p2.surename", person1 = person1, person2 = person2, relation = relation)

def getRelation(phrase):
    relation = ""
    lookups = [
        ('cas(?:ou|ado)', "casado"),
        ('não são casados', "divorciado"),
        ('namora', "namora"),
    ]

    for pattern, value in lookups:
        if re.search(pattern, phrase):
            relation = value

    return relation

    
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
    rS = r"(?:casado|casou|divorciado|divorciou|namorado|namorada|esposa|marido|não são casados|namora)"

    #Equitecar nomes e relationStatus em cada frase
    for phrase in phrases:
        ph = re.sub(r"(?:o|a|O|A|do|da) " + f"({pM})", r'{\1}:p', phrase)
        ph = re.sub(f" ({rS})", r'{\1}:r', ph)
        p.append(ph)
        #print(p)

    for phrase in p:
        if(re.search(r"{(.*?)}:r", phrase)):
            #relation = re.findall(r"{(\w+)}:r", phrase)
            relation = getRelation(phrase)
            if(re.search(r"(.*?):p", phrase)):
                result = re.findall(r"{(\w+)}:p",phrase)
                if(len(result) > 1):
                    addRelation(session, result[0], result[1], relation)
                    print(f"Pessoa 1: {result[0]} Pessoa 2: {result[1]} Estado: {relation}")   
                lastPerson = result[len(result) - 1]    




    #nome = "Kermit"
    #createNode(session,nome,nodeperson)
    #addRelation(session,"Tell ",nome,"daddychocked")

if __name__ == "__main__":
    main()