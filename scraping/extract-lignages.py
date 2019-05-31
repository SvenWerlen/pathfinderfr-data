#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html


## Configurations pour le lancement
MOCK_LIGNAGE = None
MOCK_LIGNAGE = "mocks/lignages.html"       # décommenter pour tester avec les lignages pré-téléchargées
MOCK_LIGNAGE_PAGE = None
#MOCK_LIGNAGE_PAGE = "mocks/lignage-aberrant.html"


#
# cette fonction extrait le texte du prochain élément après ...
#
def findAfter(html, afterTag, afterCond, searched):
    elements = html.find_next(afterTag, afterCond).next_siblings
    for el in elements:
        if el.name == searched:
            return el.text.strip()

#
# cette fonction extrait le texte pour une propriété <b>propriété</b> en prenant le texte qui suit
#
def findProperty(html, propName):
    for el in html:
        if el.name == 'b' and el.text.lower().startswith(propName.lower()):
            value = ""
            for e in el.next_siblings:
                if e.name == 'br':
                    break
                elif e.string:
                    value += e.string
                else:
                    value += e
            return value.replace('.','').strip()
    return None

#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = html.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

def extractSource(text):
    if text.endswith('*'):
        return "SSO"
    
    m = re.search('.+\((.+?)\).*', text)
    if m:
        found = m.group(1)
        if found == "MJRA" or found == "AM" or found == "AO" or found == "MR" or found == "DEP":
            return found
        elif found == "BofF":
            return "BOF"
        elif found == "CM":
            return "MCA"
        elif found == "CofB":
            return "COB"
        elif found == "BoA":
            return "BOA"
        elif found == "PFC":
            return "OOG"
        else:
            print("Source not found: " + found)
            exit(1)
    return "MJ"

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)

liste = []


if MOCK_LIGNAGE:
    content = BeautifulSoup(open(MOCK_LIGNAGE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen("http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.lignages.ashx").read(),features="lxml").body

lignages = content.find("div", {'presentation navmenu'}).find_all("li");
for l in lignages:
    link = l.find("a")
    if link is None:
        continue;
    
    lignage = {}
    lignage['1Nom'] = u"Lignage: " + link.text
    lignage['2Classe'] = u"Ensorceleur"
    lignage['4Source'] = extractSource(l.text)
    lignage['5Niveau'] = 1
    lignage['6Description'] = ""
    lignage[u'7Référence'] = "http://www.pathfinder-fr.org/Wiki/" + link["href"]
    lignage['EMPTY'] = ""
    
    print("Processing: " + link["href"])

    if MOCK_LIGNAGE_PAGE:
        lignageHTML = BeautifulSoup(open(MOCK_LIGNAGE_PAGE),features="lxml").body
    else:
        lignageHTML = BeautifulSoup(urllib.request.urlopen(lignage[u'7Référence']).read(),features="lxml").body
    
    descr = ""
    for t in lignageHTML.find_all('i'):
        descr = t.text.strip()
        if descr.startswith('*'):
            continue
        break
    descr = descr.replace('\n','').strip()
    
    # additional information
    skill = findProperty(lignageHTML.find(id='PageContentDiv'),u'Compétence de classe')
    if skill == None:
        print("Skill not found")
        exit(1)
    spells = findProperty(lignageHTML.find(id='PageContentDiv'),u'Sorts supplémentaires')
    if spells == None:
        print("Spells not found")
        exit(1)
    feats = findProperty(lignageHTML.find(id='PageContentDiv'),u'Dons supplémentaires')
    if feats == None:
        print("Feats not found")
        exit(1)
    arcans = findProperty(lignageHTML.find(id='PageContentDiv'),u'Arcanes de lignage')
    if arcans == None:
        print("Arcans not found")
        exit(1)
    
    descr += "\n\nCOMPÉTENCE DE CLASSE: " + skill
    descr += "\n\nSORTS SUPPLÉMENTAIRES: " + spells
    descr += "\n\nDONS SUPPLÉMENTAIRES: " + feats
    descr += "\n\nARCANES DE LIGNAGE: " + arcans
    
    pouvoirs = jumpTo(lignageHTML, 'h2',{'class':'separator'}, u"Pouvoirs de lignage")
    #if pouvoirs is None:
    #    print("NOT FOUND!!")
    #    continue
    #for p in pouvoirs:
    #    if p.name is None or p.name == 'a' or p.name == 'b' or p.name == 'i':
    #        lignage['6Description'] += p.string
    #    elif(p.name == 'br'):
    #        lignage['6Description'] += '\\n'
    #    elif(p.name == 'h2'):
    #        break
    
    lignage['6Description'] = descr
    liste.append(lignage)

#exit(1)

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('2Classe','Classe')
yml = yml.replace('4Source','Source')
yml = yml.replace('5Niveau','Niveau')
yml = yml.replace("6Description: '",'Description: "')
yml = yml.replace("\\n\\n:'",'"')
yml = yml.replace("\\n\\n:'",'"')
yml = yml.replace(u'7Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
