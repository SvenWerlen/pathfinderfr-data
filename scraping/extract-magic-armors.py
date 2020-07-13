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
#MOCK_MAGIC = "mocks/magic-armors.html"                  # décommenter pour tester avec les armures pré-téléchargées
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-bouclier-elysien.html"      # décommenter pour tester avec détails pré-téléchargé

TEXTE = 'Si l’armure ou le bouclier bénéficie seulement d’un bonus d’altération, son niveau de lanceur de sorts est égal à trois fois son bonus. Si l’objet possède un bonus d’altération ainsi que des propriétés magiques, le plus haut niveau de lanceur de sorts entre les deux est celui qui doit être considéré.\n\nBoucliers. Le bonus d’altération d’un bouclier magique se cumule avec le bonus d’altération d’une armure magique. Le bonus d’altération du bouclier n’est pas comptabilisé dans le jet d’attaque ou de dégâts dans le cas d’un coup de bouclier. La propriété spéciale d’attaque confère un bonus d’altération de +1 aux jets d’attaque et de dégâts avec un bouclier (voir la description de la capacité spéciale "Attaque").'

FIELDS = ['Nom', 'Type', 'Prix', 'Source', 'Emplacement', 'Poids', 'Aura', 'NLS', 'Conditions', 'Coût', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']

liste = []


# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Armures%20magiques.ashx"
TYPE = "Armure/Bouclier"
IGNORE = ["Armure spécifique","Bouclier spécifique"]
TABLEDEF = {
    1: [4,5,"", {'descr': TEXTE}],
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

tables = content.find_all('table',{'class':['tablo col1centre']})

liste = []

print("Extraction des armures magiques...")

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
        
        data = {"nom": cleanName(nom), "prix": prix.strip(), "descr": "", "descrHTML": ""}
        
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
            descrHTML = data['descrHTML']
            
            if len(data['descr']) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
        
        element = {}
        element["Nom"] = data["nom"]
        element["Type"] = TYPE
        element["Prix"] = data["prix"]
        element["Source"] = "MJ"
        element["Description"] = data["descr"]
        element["DescriptionHTML"] = data["descrHTML"]
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
