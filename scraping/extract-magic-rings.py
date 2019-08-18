#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import table2text, extractBD_Type1, extractBD_Type2, html2text, cleanName, mergeYAML

## Configurations pour le lancement
MOCK_MAGIC = None
#MOCK_MAGIC = "mocks/magic-rings.html"                  # décommenter pour tester avec les anneaux pré-téléchargées
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-ring-protection.html"      # décommenter pour tester avec détails pré-téléchargé

TEXTE = ''

FIELDS = ['Nom', 'Type', 'Prix', 'Source', 'Emplacement', 'Poids', 'Aura', 'NLS', 'Conditions', 'Coût', 'Description', 'Référence' ]
MATCH = ['Nom']


liste = []


# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Anneaux%20magiques.ashx"
TYPE = "Anneau"
IGNORE = ["Arme spécifique"]
TABLEDEF = {
    1: [4,5,"Anneau: "],
    2: [4,5,"Anneau "],
}


if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


propList = []

tables = content.find_all('table',{'class':['tablo col1centre']})

liste = []

print("Extraction des anneaux magiques...")

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
                nom = html2text(td)
                href = td.find('a')
                if href:
                    href = href['href']
            elif columnIdx == TABLEDEF[tableIdx][1]:
                prix = html2text(td)
        
        # sauter les entrées du type "relancer le dé"
        if u"le dé" in nom:
            continue
        
        # ignorer certaines entrées (référence à un autre tableau dans la page)
        if nom in IGNORE:
            continue
        else:
            nom = TABLEDEF[tableIdx][2] + nom
        
        # référence de base
        reference = REFERENCE
        
        data = {"nom": cleanName(nom), "prix": prix.strip(), "descr": ""}
        
        if len(TABLEDEF[tableIdx]) == 4:
            data = { **data, **TABLEDEF[tableIdx][3] }
        
        # débogage
        print("Traitement de %s..." % nom.strip())
        
        # get description from same page
        if href and "#" in href and not "NOTE" in href:
            ref = "#" + href.split('#')[1]
            jumpTo = content.find('a',{'href':ref})
            if jumpTo is None:
                print("Lien invalide: %s" % href)
                exit(1)
            data = {**data, **extractBD_Type1(jumpTo.find_next('div',{'class':['BD']}))}
            
            reference = PATHFINDER + href
            if len(data['descr']) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
        
        elif href and not "#" in href:
            # récupérer le détail d'un objet
            if MOCK_MAGIC_ITEM:
                page = BeautifulSoup(open(MOCK_MAGIC_ITEM),features="lxml").body
            else:
                page = BeautifulSoup(urllib.request.urlopen(PATHFINDER + href).read(),features="lxml").body
                
            reference = PATHFINDER + href
            data = {**data, **extractBD_Type2(page.find('div',{'class':['BD']}))}
            descr = data['descr']
            
            if len(data['descr']) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
        
        element = {}
        element["Nom"] = data["nom"]
        element["Type"] = TYPE
        element["Prix"] = data["prix"]
        element["Source"] = "MJ"
        element["Description"] = data["descr"]
        element["Référence"] = reference
        
        # infos additionnelles
        if "emplacement" in data:
            element["Emplacement"] = data["emplacement"]
        if "poids" in data:
            element["Poids"] = data["poids"]
        if "aura" in data:
            element["Aura"] = data["aura"]
        if "nls" in data:
            # NLS parfois variable
            if isinstance(data["nls"], int):
                element["NLS"] = data["nls"]
            else:
                element["Description"] = "NLS: " + data["nls"] + "\n\n" + element["Description"]
        if "conditions" in data:
            element["Conditions"] = data["conditions"]
        if "coût" in data:
            element["Coût"] = data["coût"]
        
        liste.append(element)
    
#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic.yml", MATCH, FIELDS, HEADER, liste)
