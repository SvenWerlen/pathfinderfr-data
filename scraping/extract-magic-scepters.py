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
#MOCK_MAGIC = "mocks/magic-scepters.html"                  # décommenter pour tester avec les sceptres pré-téléchargées
MOCK_MAGIC_META = None
#MOCK_MAGIC_META = "mocks/magic-scepters-meta.html"                  # décommenter pour tester avec les sorts de métamagie pré-téléchargés
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-carreau.html"      # décommenter pour tester avec détails pré-téléchargé

TEXTE = 'Si l’arme bénéficie seulement d’un bonus d’altération, son niveau de lanceur de sorts est égal à trois fois son bonus. Si l’objet possède un bonus d’altération ainsi que des propriétés magiques, le plus haut niveau de lanceur de sorts entre les deux est celui qui doit être considéré. Armes à distance et projectiles. \n\nLe bonus d’altération d’une arme à projectiles ne se cumule pas avec le bonus d’altération de ses munitions. Seule la plus haute valeur est prise en compte.'

FIELDS = ['Nom', 'Type', 'Prix', 'Source', 'Emplacement', 'Poids', 'Aura', 'NLS', 'Conditions', 'Coût', 'Description', 'Référence' ]
MATCH = ['Nom']


liste = []


# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Sceptres%20magiques.ashx"
REFERENCE_META = "Pathfinder-RPG.Sceptre%20de%20m%c3%a9tamagie.ashx"
TYPE = "Sceptre"
IGNORE = []
TABLEDEF = {
    1: [3,4,""],
    2: [3,4,""],
}


if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body

if MOCK_MAGIC_META:
    meta = BeautifulSoup(open(MOCK_MAGIC_META),features="lxml").body
else:
    meta = BeautifulSoup(urllib.request.urlopen(PATHFINDER + REFERENCE_META).read(),features="lxml").body


##
## Load all metamagie
##
metalist = []
tables = meta.find_all('div',{'class':['BD']})
for t in tables:
    data = extractBD_Type2(t)
    # extract property
    data['prop'] = data['nomAlt'].split(', ')[1].lower()
    metalist.append(data)

propList = []

tables = content.find_all('table',{'class':['tablo col1centre']})

print("Extraction des sceptres magiques...")

liste = []
exists = []

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
        
        
        # get description from metamagie
        if href and href.startswith(REFERENCE_META):
            # try to find matching metamagie
            found = None
            for m in metalist:
                if m['prop'] in data['nom'].lower():
                    found = m
            
            if found:
                reference = PATHFINDER + REFERENCE_META
                data = {**data, **found}
            else:
                print("Correspondance non-trouvé pour %s" % data["nom"])
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
        element["Nom"] = data["nomAlt"]
        element["Type"] = TYPE
        element["Prix"] = data["prixAlt"]
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
                
        if not data["nomAlt"] in exists:
            exists.append(data["nomAlt"])
            liste.append(element)
    
#exit(1)


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic.yml", MATCH, FIELDS, HEADER, liste)
