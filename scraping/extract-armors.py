#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, mergeYAML

## Configurations pour le lancement
URL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20armures.ashx"
URLDET = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Descriptions%20individuelles%20des%20armures.ashx"
MOCK_W = None
#MOCK_W = "mocks/armors.html"           # décommenter pour tester avec les armes pré-téléchargées
MOCK_WD = None
#MOCK_WD = "mocks/armors-details.html"  # décommenter pour tester avec les armes pré-téléchargées

FIELDS = ['Nom', 'Catégorie', 'Source', 'Prix', 'Bonus', 'BonusDexMax', 'Malus', 'ÉchecProfane', 'Vit9m', 'Vit6m', 'Poids', 'Description', 'Référence' ]
MATCH = ['Nom']


liste = []


if MOCK_W:
    content = BeautifulSoup(open(MOCK_W),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

tables = content.find_all('table',{'class':'tablo'})

armor = {}
type = ""

print("Extraction des armures...")

for t in tables:
    rows = t.find_all('tr')
    for r in rows:
        cols = r.find_all('td')
        if 'class' in r.attrs and 'premier' in r.attrs['class']:
            type = r.text.strip()
            type = type[0].upper() + type[1:].lower()
            # hack (fonctionne par hasard ;-)
            type = type.replace('s','').replace('2','')
            print("Extraction %s ..." % type)
            continue
        if len(cols) == 10:
            # Name & Reference
            nameLink = cols[0].find('a')
            if not nameLink is None:
                armor['Nom'] = nameLink.text.strip()
                armor['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
            else:
                armor['Nom'] = cols[0].text.strip()
                armor['Référence'] = URL
            # Others
            armor['Nom'] = armor['Nom'].replace('’','\'')
            armor['Catégorie'] = type
            armor['Prix'] = cols[1].text.strip()
            armor['Bonus'] = cols[2].text.strip()
            armor['BonusDexMax'] = cols[3].text.strip()
            armor['Malus'] = cols[4].text.strip()
            armor['ÉchecProfane'] = cols[5].text.strip()
            armor['Vit9m'] = cols[6].text.strip()
            armor['Vit6m'] = cols[7].text.strip()
            armor['Poids'] = cols[8].text.strip()
            armor['Complete'] = False

            armor['Source'] = "MJ"
            if cols[9].text.strip() == "UC":
                armor['Source'] = "AG"
            liste.append(armor)
            armor = {}

# last element



#
# cette fonction ajoute les infos additionelles
#
def addInfos(liste, name, source):
    names = []
    # ugly fix
    name = name.replace('’','\'')
    if name.endswith('.'):
        name = name[:-1]
    if(name == "Habits rembourrés"):
        names = ["Vêtements rembourrés".lower()]
    elif(name == "Armure lamellaire"):
        names = ["Armure lamellaire (acier)".lower(),"Armure lamellaire (fer)".lower(),"Armure lamellaire (cuir)".lower(),"Armure lamellaire (corne)".lower(),"Armure lamellaire (pierre)".lower()]
    elif(name == "Armure à plaques ou de plaques"):
        names = ["Armure de plaques".lower()]
    elif(name == "Écu en bois ou en acier"):
        names = ["Écu (bois)".lower(),"Écu (acier)".lower()]
    elif(name == "Rondache en bois ou en acier"):
        names = ["Rondache (bois)".lower(),"Rondache (acier)".lower()]
    elif(name == "Madu en acier ou en cuir"):
        names = ["Madu (cuir)".lower(),"Madu (acier)".lower()]
    elif(name == "Rondache à manipulation rapide ou de preste usage, en bois ou en acier"):
        names = ["Rondache de preste usage (bois)".lower(),"Rondache de preste usage (acier)".lower()]
    elif(name == "Gantelet d'armes (ou gantelet à fixations)"):
        names = ["Gantelet d'armes".lower()]
    elif(name == "Armure à plaques flexible ou agile"):
        names = ["Armure de plaques flexible".lower()]
    elif(name == "Armure de peau"):
        names = ["Armure en peau".lower()]
    else:
        names = [name.lower()]

    # add infos to existing armors in list
    found = False
    for l in liste:
        if l['Nom'].lower() in names:
            l['Complete'] = True
            l['Description'] = descr.strip()
            if not source is None:
                l['Source'] = source
            found = True
    if not found:
        print("COULD NOT FIND : '" + name + "'");


if MOCK_WD:
    content = BeautifulSoup(open(MOCK_WD),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(URLDET).read(),features="lxml").body

section = jumpTo(content, 'h1',{'class':'separator'}, "Armures classiques")

newObj = True
name = ""
descr = ""
source = None
sourceNext = None
for s in section:
    if s.name == 'div':
        for e in s.children:
            if e.name == 'h2' or e.name == 'b':
                if not newObj:
                    addInfos(liste, name, sourceNext)
                sourceNext = source

                if e.name == 'h2':
                    newObj = True
                    source = None
                else:
                    name = e.text.strip()
                    source = None
                    descr = ""
                    newObj = False
            elif e.name == 'br':
                descr += "\n"
            elif e.name is None or e.name == 'a':
                if not e.string is None:
                    descr += e.string.replace('\n',' ')
            elif e.name == 'i':
                descr += e.text
            elif e.name == 'div':
                for c in e.children:
                    if c.name == 'img':
                        if('logoAPG' in c['src']):
                            source = 'MJRA'
                        elif('logoUC' in c['src']):
                            source = 'AG'
                        elif('logoMCA' in c['src']):
                            source = 'MCA'
                        elif('logoAE' in c['src']):
                            source = 'AE'
                        else:
                            print(c['src'])
                            exit(1)

addInfos(liste, name, sourceNext)

for l in liste:
    if not l['Complete']:
        print("INCOMPLETE: '" + l['Nom'] + "'");
    del l['Complete']


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/armures.yml", MATCH, FIELDS, HEADER, liste)
