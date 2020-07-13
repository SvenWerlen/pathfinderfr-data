#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import findProperty, jumpTo, extractLevel, html2text, mergeYAML

## Configurations pour le lancement
MOCK_LIGNAGE = None
#MOCK_LIGNAGE = "mocks/lignages.html"       # décommenter pour tester avec les lignages pré-téléchargées
MOCK_LIGNAGE_PAGE = None
#MOCK_LIGNAGE_PAGE = "mocks/lignage-aberrant.html"

URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.lignages.ashx"
FIELDS = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom', 'Classe', 'Archétype']


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


liste = []
listePouvoirs = []

print("Extraction des aptitude (lignages)...")

if MOCK_LIGNAGE:
    content = BeautifulSoup(open(MOCK_LIGNAGE),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

section = jumpTo(content, 'h2',{'class':'separator'}, "Les lignages d'ensorceleurs¶")

for s in section:
  if s.name == "div" and "navmenu" in s.attrs['class']:
    lignages = s.find_all("li");
    for l in lignages:
        link = l.find("a")
        if link is None:
            continue;
        
        lignage = {}
        lignage['Nom'] = "Lignage: " + link.text
        lignage['Classe'] = "Ensorceleur"
        lignage['Source'] = extractSource(l.text)
        lignage['Niveau'] = 1
        lignage['Description'] = ""
        lignage['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + link["href"]
        
        print("Processing: " + link["href"])

        if MOCK_LIGNAGE_PAGE:
            lignageHTML = BeautifulSoup(open(MOCK_LIGNAGE_PAGE),features="lxml").body
        else:
            lignageHTML = BeautifulSoup(urllib.request.urlopen(lignage['Référence']).read(),features="lxml").body
        
        # Sauter à la description
        descr = ""
        descrHTML = ""
        for t in lignageHTML.find_all('i'):
            descr = t.text.strip()
            if descr.startswith('*'): # Ignorer les références à la source (Ex: * Source semi-officielle)
                continue
            break
        descr = descr.replace('\n','').strip()
        descrHTML = descr
        
        # additional information
        skill = findProperty(lignageHTML.find(id='PageContentDiv'),'Compétence de classe', False)
        if skill == None:
            print("Skill not found")
            exit(1)
        spells = findProperty(lignageHTML.find(id='PageContentDiv'),'Sorts supplémentaires', False)
        if spells == None:
            print("Spells not found")
            exit(1)
        feats = findProperty(lignageHTML.find(id='PageContentDiv'),'Dons supplémentaires', False)
        if feats == None:
            feats = findProperty(lignageHTML.find(id='PageContentDiv'),'Don supplémentaire', False)
        if feats == None:
            print("Feats not found")
            exit(1)
        arcans = findProperty(lignageHTML.find(id='PageContentDiv'),'Arcanes de lignage', False)
        if arcans == None:
            print("Arcans not found")
            exit(1)
        
        descr += "\n\nCOMPÉTENCE DE CLASSE: " + skill
        descr += "\n\nSORTS SUPPLÉMENTAIRES: " + spells
        descr += "\n\nDONS SUPPLÉMENTAIRES: " + feats
        descr += "\n\nARCANES DE LIGNAGE: " + arcans
        
        descrHTML += "<br/><br/><b>Compétences de classe:</b> " + skill
        descrHTML += "<br/><br/><b>Sorts supplémentaires:</b> " + spells
        descrHTML += "<br/><br/><b>Dons supplémentaires:</b> " + feats
        descrHTML += "<br/><br/><b>Arcanes de lignage:</b> " + arcans
        
        lignage['Description'] = descr
        lignage['DescriptionHTML'] = descrHTML
        liste.append(lignage)
        
        ## Pouvoirs de lignage
        
        pouvoirs = jumpTo(lignageHTML, 'h2',{'class':'separator'}, "Pouvoirs de lignage")
        if pouvoirs is None:
            print("Pouvoirs de lignages not found!")
            exit(1)
        for p in pouvoirs:
            if p.name == 'h2':
                break
            if p.name == 'b':
                pouvoirName = p.text[:-1] # retire le point à la fin du nom
                pouvoir = {}
                pouvoir['Nom'] = "Lignage " + link.text + ": " + pouvoirName
                pouvoir['Classe'] = "Ensorceleur"
                pouvoir['Source'] = lignage['Source']
                pouvoir['Niveau'] = 1
                pouvoir['Description'] = findProperty(jumpTo(lignageHTML, 'h2',{'class':'separator'}, "Pouvoirs de lignage"), pouvoirName, False)
                pouvoir['DescriptionHTML'] = pouvoir['Description']
                pouvoir['Référence'] = lignage['Référence']
                pouvoir['Niveau'] = extractLevel(pouvoir['Description'], 30)
                
                if pouvoir['Description'] == None:
                    print("Invalid description for pouvoir de lignage")
                    exit(1)
                
                listePouvoirs.append(pouvoir)

#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, liste)
mergeYAML("../data/classfeatures.yml", MATCH, FIELDS, HEADER, listePouvoirs)
