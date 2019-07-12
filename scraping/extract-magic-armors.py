#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import table2text
from libhtml import extractBD

## Configurations pour le lancement
MOCK_MAGIC = None
MOCK_MAGIC = "mocks/magic-armors.html"       # décommenter pour tester avec les armures pré-téléchargées



liste = []

# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Armures%20magiques.ashx"
TYPE = "Armure/Bouclier"
IGNORE = ["Armure spécifique","Bouclier spécifique"]
TABLEDEF = {
    1: [4,5,""],
    2: [4,5,"Armure: "],
    3: [4,5,"Armure: "],
    4: [4,5,"Bouclier: "],
    5: [4,5,""],
    6: [3,4,""],
    7: [4,5,""],
    8: [2,3,""],
    9: [1,2,""],
}


if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


propList = []
proprietes = content.find_all('div',{'class':['BD']})

for prop in proprietes:
    propList.append(extractBD(prop))
    

tables = content.find_all('table',{'class':['tablo col1centre']})

liste = []

tableIdx = 0
for t in tables:
    tableIdx += 1
    caption = t.find('caption').text
    for tr in t.find_all('tr'):
        if tr.has_attr('class') and (tr['class'][0] == 'titre' or tr['class'][0] == 'soustitre'):
            continue
        
        columnIdx = 0
        for td in tr.find_all('td'):
            columnIdx += 1
            if columnIdx == TABLEDEF[tableIdx][0]:
                nom = TABLEDEF[tableIdx][2] + td.text
                href = td.find('a')
                if href:
                    href = href['href']
            elif columnIdx == TABLEDEF[tableIdx][1]:
                prix = td.text
        
        # sauter les entrées du type "relancer le dé"
        if u"le dé" in nom:
            continue
        
        # ignore some entries
        if nom in IGNORE:
            continue
        
        # reference
        reference = REFERENCE
        
        # get description from same page
        descr = ""
        if href and "#" in href and not "NOTE" in href:
            ref = "#" + href.split('#')[1]
            jumpTo = content.find('a',{'href':ref})
            if jumpTo is None:
                print("Lien invalide: %s" % href)
                exit(1)
            data = extractBD(jumpTo.find_next('div',{'class':['BD']}))
            descr = data['descr']
            reference = REFERENCE + href
            if len(descr) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
        
        elif href and not "#" in href:
            page = BeautifulSoup(urllib.request.urlopen(PATHFINDER + href).read(),features="lxml").body
            data = extractBD(page.find('div',{'class':['BD']}))
            descr = data['descr']
            reference = PATHFINDER + href
            if len(descr) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
        
        element = {}
        element["1Nom"] = nom.strip()
        element["2Type"] = TYPE
        element["3Prix"] = prix.strip()
        element["4Source"] = "MJ"
        element["6Description"] = descr
        element["7Référence"] = reference
        element["EMPTY"] = ""
        liste.append(element)
    
#exit(1)

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('1Nom','Nom')
yml = yml.replace('2Type','Type')
yml = yml.replace('3Prix','Prix')
yml = yml.replace('4Source','Source')
yml = yml.replace('6Description','Description')
yml = yml.replace(u'7Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)

