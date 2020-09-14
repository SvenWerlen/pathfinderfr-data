#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import *

## Configurations pour le lancement
URLS = [ "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Armes%20alchimiques.ashx"]

MOCK_W = None
#MOCK_W = "mocks/weapons.html"           # décommenter pour tester avec les armes pré-téléchargées
MOCK_WD = None
#MOCK_WD = "mocks/weapons-details.html"  # décommenter pour tester avec les armes pré-téléchargées


FIELDS = ['Nom', 'Catégorie', 'Sous-catégorie', 'Source', 'Prix', 'Artisanat', 'Dégâts', 'Critique', 'Portée', 'Poids', 'Type', 'Spécial', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']


liste = []

for URL in URLS:
    if MOCK_W:
        content = BeautifulSoup(open(MOCK_W),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

    sections = content.find_all('h2',{'class':'separator'})

    type1 = []

    # extraction des types
    for s in sections:
        if s.text.startswith("Accès rapide"):
            continue
        section = cleanSectionName(s.text)
        section = section.replace("Les armes", "Arme").replace("s","")
        type1.append(section)

    tables = content.find_all('table',{'class':'tablo'})

    weapon = {}
    type2 = ""

    print("Extraction des armes...")

    idx = 0
    parent = None
    for t in tables:
        rows = t.find_all('tr')
        for r in rows:
            cols = r.find_all('td')
            if 'class' in r.attrs and 'titre' in r.attrs['class']:
                continue
            if len(cols) == 1 and 'class' in r.attrs and 'premier' in r.attrs['class']:
                type2 = r.text.strip()
                type2 = type2[0].upper() + type2[1:].lower()
                type2 = type2.replace('Armes','Arme')
                print("Extraction %s ..." % type2)
                continue
            if len(cols) == 9:
                # Name & Reference
                nameLink = cols[0].find('a')
                weapon['Nom'] = cols[0].text.strip()
                if not nameLink is None:
                    weapon['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
                else:
                    weapon['Référence'] = URL
                
                # Others
                weapon['Nom'] = weapon['Nom'].replace('’','\'').replace('*','')
                if cols[0].text.startswith("  "):
                    weapon['Nom'] = "%s (%s)" % (parent, weapon['Nom'])
                weapon['Catégorie'] = type1[idx]
                weapon['Sous-catégorie'] = type2
                weapon['Prix'] = cols[1].text.strip()
                weapon['Artisanat'] = cols[2].text.strip()
                weapon['Dégâts'] = cols[3].text.strip()
                weapon['Critique'] = cols[4].text.strip()
                weapon['Portée'] = cols[5].text.strip()
                weapon['Poids'] = cols[6].text.strip()
                weapon['Type'] = cols[7].text.strip()
                weapon['Spécial'] = cols[8].text.strip()
                weapon['Complete'] = False
                weapon['Source'] = "MJ"
                
                if len(weapon['Prix']) == 0:
                    parent = weapon['Nom']
                    continue
                
                liste.append(weapon)
                weapon = {}
        
        idx+=1


#
# cette fonction ajoute les infos additionelles
#
def addInfos(liste, name, source):
    name = name.split(" (")[0]
    names = []
    if name == "Ballerine banshie" or name == "Fontaine de flammes" or name == "Fontaine stellaire":
        names.append(("%s d'artifice" % name).lower())
    elif name == "Etoiles d'artifice":
        names.append("Etoile d'artifice".lower())
    elif name == "Poings de verre":
        names.append("Fioles pour poings de verre".lower())
        names.append(name.lower())
    else:
        names.append(name.lower())
    

    # add infos to existing weapon in list
    found = False
    for l in liste:
        elName = l['Nom'].split(" (")[0].lower()
        if (elName.startswith("flèche ") and name == "Flèches alchimiques") or (elName in names):
            l['Complete'] = True
            l['Description'] = descr.strip()
            l['DescriptionHTML'] = descrHTML
            if not source is None:
                l['Source'] = source
            found = True
    if not found:
        print("- une description existe pour '" + name + "' mais pas le sommaire!");



section = jumpTo(content, 'h2',{'class':'separator'}, u"Armes alchimiques")
    
newObj = True
name = ""
descr = ""
descrHTML = ""
source = None
sourceNext = None
for s in section:
    if s.name == 'h3':
        if not newObj:
            addInfos(liste, name, sourceNext)

        sourceNext = source
        newObj = False
        name = cleanSectionName(s.text.strip())
        descr = ""
        descrHTML = ""
        source = None

    else:
        descr += html2text(s)
        descrHTML += html2text(s, True, 2)
        if s.name == 'div' or s.name == 'a':
          sourceFound = extractSource(s)
          if sourceFound:
              source = sourceFound

addInfos(liste, name, sourceNext)


for l in liste:
    if not l['Complete']:
        print("- aucune description n'existe pour '" + l['Nom'] + "'!");
    del l['Complete']


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/armes-alchimiques.yml", MATCH, FIELDS, HEADER, liste)
