#!/usr/bin/env python3

import re
import subprocess
import sys
import fileinput 
from neo4j import GraphDatabase
import os.path #used to read files
import requests as req #use to establish connection with web
from getopt import getopt


def formatText(text):

    listPhrases = []

    #Formats the text by paragraphs and adds them to listParagraphs for later use
    aux = re.sub(r"([.!?]) ", r"\1SeparadorA1IPLN", text)
    listPhrases = aux.split("SeparadorA1IPLN")

    phrases = []

    for phrase in listPhrases:
        phrases.append(phrase)

    return phrases

#creates a node if it does not exist
def createNode(driver,person):
    with driver.session() as session:
        session.run("MERGE (p:Person {surename: $person}) RETURN p.surename", person = person)

#adds a relatioship to two existing nodes, from person1 to person2
def addRelation(driver,person1, person2, relation):
    with driver.session() as session:
        session.run("MATCH (p1:Person { surename: $person1 }),(p2:Person { surename: $person2 }) MERGE (p1)-[r:"+relation +"]->(p2) RETURN p1.surename, type(r), p2.surename", person1 = person1, person2 = person2, relation = relation)

#clears all data from database
def clearTable(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

#returns relation depending on received regex
def getRelation(phrase):
    relation = ""
    lookups = [
        ('cas(?:ou|ado|ada|aram)', "casado"),
        ('não são casados', "divorciado"),
        ('divorci(?:ado|ados|ada|ou|aram)',"divorciado"),
        ('namor(?:a|ado|ada)', "namora"),
        ('namor(?:ou|aram)',"exnamorado"),
        ('irmãos', "irmão"),
        ('irmão', "irmão"),
        ('esposa',"esposa"),
        ('marido',"marido"),
        ('amig(?:a|o|as|os)', "amigo")
    ]

    for pattern, value in lookups:
        if re.search(pattern, phrase):
            relation = value
    return relation

#creates list of names
def createNameList(texto):
    if not os.path.exists('names.txt'):
        f = open("names.txt", "w")
        x = req.get("https://pt.wikipedia.org/wiki/Lista_de_nomes_portugueses")
        text = x.text
        names = re.findall(r"<i>infopedia</i> ([A-ZÀ-Ü][a-zà-ü]*)</a>.</span>", text)
        for n in re.findall(r"<li>([A-ZÀ-Ü][a-zà-ü]*)</li>", text):
            if (len(n) > 1):
                if (n not in names):
                    names.append(n)

        for n in (re.findall(r"<li>([A-ZÀ-Ü][a-zà-ü]*)<sup id=\"cite_ref-(?:.*?)\" class=\"reference\">", text)):
            if (len(n) > 1):
                if (n not in names):
                    names.append(n)
        for n in names:
            f.write(n + "\n")
            f.wr
        f.close()
    else:
        for line in fileinput.input("names.txt"):
            nameList.append(line)

#main function
def main():
    opts, resto = getopt(sys.argv[1:], "fc")
    dop = dict(opts)

    #Initiate connection and create session
    driver = GraphDatabase.driver(uri="bolt://localhost:7687" , auth=("neo4j", "eheh"))
    clearTable(driver)


    text = ""
    # Reads file
    for line in fileinput.input(resto):
        text += line


    if "-f" in dop:
        createNameList(resto)

    phrases = []
    phrases = formatText(text)
    p = []
    pM = r"(?:[A-ZÀ-Ü]\w+|[A-ZÀ-Ü]\.|[A-ZÀ-Ü][a-z]\.)"
    d = r"(?:da|do|de|dos|das)"
    nP = f"{pM}(?: {pM}| {d} {pM})*"
    rS = r"(?:cas(?:ado|ada|ou)|divorci(?:ado|ada|ou|aram)|namor(?:a|ou|aram|ada|ado)|esposa|marido|não são casados|irmãos|irmão|amig(?:a|o|as|os))"

    #Tags names and relationships on each phrase
    for phrase in phrases:
        ph = re.sub(r"(?:o|a|O|A|do|da) " + f"({nP})", r'{\1}:p', phrase)
        ph = re.sub(f" ({rS})", r'{\1}:r', ph)
        p.append(ph)

    #iterates each phrase
    for phrase in p:
        #looks for a relation
        if(re.search(r"{(.*?)}:r", phrase)):
            relation = getRelation(phrase)
            #looks for subjects, needs a minimal of two to work
            if(re.search(r"(.*?):p", phrase)):
                result = re.findall(r"{(\w+(?: \w+)*)}:p",phrase)
                if(len(result) > 1):
                    createNode(driver,result[0])
                    createNode(driver,result[1])
                    addRelation(driver, result[0], result[1], relation)
                #if there's more than 2 subjects we assume they are all related
                if(len(result) > 2):
                    for i in range(0, len(result)):
                        createNode(driver, result[i])
                        if not i is 0:
                            for x in range(0,i):
                                addRelation(driver, result[x],result[i],relation)

if __name__ == "__main__":
    main()  

