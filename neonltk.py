#!/usr/bin/env python3

import re
import subprocess
import sys
import fileinput 
from neo4j import GraphDatabase #import of neo4j
import nltk
from nltk.tokenize import word_tokenize


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
def createNode(driver,person):
    with driver.session() as session:
        session.run("MERGE (p:Person {surename: $person}) RETURN p.surename", person = person)

#adds a relatioship to two existing nodes, from person1 to person2
def addRelation(driver,person1, person2, relation):
    with driver.session() as session:
        session.run("MATCH (p1:Person { surename: $person1 }),(p2:Person { surename: $person2 }) MERGE (p1)-[r:"+relation +"]->(p2) RETURN p1.surename, type(r), p2.surename", person1 = person1, person2 = person2, relation = relation)

def cleanTable(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

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
    cleanTable(graphdb)


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
        #text = word_tokenize(phrase,language="portuguese")
        #tokens = nltk.pos_tag(text)
        #print(tokens)
        ph = re.sub(r"(?:(o|a|O|A|do|da)) " + f"({pM})", r' {\1}:s {\2}:p', phrase)
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
                    createNode(graphdb,result[0])
                    createNode(graphdb,result[1])
                    addRelation(graphdb, result[0], result[1], relation)
                    #print(f"Pessoa 1: {result[0]} Pessoa 2: {result[1]} Estado: {relation}")
                #elif len(result > 2):
            lastPerson = result[len(result) - 1]    

if __name__ == "__main__":
    main()