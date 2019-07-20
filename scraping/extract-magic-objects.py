#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import table2text, extractBD_Type1, extractBD_Type2, html2text, cleanName

## Configurations pour le lancement
MOCK_MAGIC = None
#MOCK_MAGIC = "mocks/magic-objets.html"                  # décommenter pour tester avec les objets merveilleux pré-téléchargées
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-ailes-vol.html"      # décommenter pour tester avec détails pré-téléchargé
#MOCK_MAGIC_ITEM = "mocks/magic-casque-comprehension.html"      # décommenter pour tester avec détails pré-téléchargé

TEXTE = ''

liste = []


# first = column with name
# second = column with cost
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Liste%20alphab%c3%a9tique%20des%20objets%20merveilleux.ashx"
TYPE = "Objet merveilleux"


if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


propList = []

multicol = content.find_all('div',{'class':['article_3col']})

liste = []

found = False
for m in multicol:
    for link in m.find_all('a'):
        
        # extraire adresse URL
        reference = PATHFINDER + link['href']
                
        # extraire nom
        nom = link.text.strip()
        
        # jump
        #if nom == "Solvant universel":
        #    found = True
        
        #if not found:
        #    continue
        
        # skip unknown links
        if('class' in link.attrs and 'unknownlink' in link['class']):
            continue

        
        # débogage
        #print("Traitement de %s..." % nom.strip())
        
        # récupérer le détail d'un objet
        if MOCK_MAGIC_ITEM:
            page = BeautifulSoup(open(MOCK_MAGIC_ITEM),features="lxml").body
        else:
            try:
                page = BeautifulSoup(urllib.request.urlopen(reference).read(),features="lxml").body
                
                pageNotFound = page.find('h1',{'class':['pagetitlesystem']})
                if(pageNotFound and pageNotFound.text() == 'Page Not Found'):
                    continue
                
            except:
                #print("Page doesn't exist! Skipping...")
                continue
            
        data = {**extractBD_Type2(page.find('div',{'class':['BD']}))}
        descr = data['descr']
        
        if len(data['descr']) == 0:
            print("Description invalide pour: %s" % href)
            exit(1)
        
        element = {}
        element["01Nom"] = data["nomAlt"] # prendre le nom de la page détaillée
        element["02Type"] = TYPE
        element["03Prix"] = data["prixAlt"] # prendre le prix de la page détaillée
        element["04Source"] = "MJ"
        element["20Description"] = data["descr"]
        element["21Référence"] = reference
        
        # infos additionnelles
        if "emplacement" in data:
            element["05Emplacement"] = data["emplacement"]
        if "poids" in data:
            element["06Poids"] = data["poids"]
        if "aura" in data:
            element["07Aura"] = data["aura"]
        if "nls" in data:
            # NLS parfois variable
            if isinstance(data["nls"], int):
                element["08NLS"] = data["nls"]
            else:
                element["20Description"] = "NLS: " + data["nls"] + "\n\n" + element["20Description"]
        if "conditions" in data:
            element["09Conditions"] = data["conditions"]
        if "coût" in data:
            element["10Coût"] = data["coût"]
        
        element["EMPTY"] = ""
        liste.append(element)
    
#exit(1)

yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('01Nom','Nom')
yml = yml.replace('02Type','Type')
yml = yml.replace('03Prix','Prix')
yml = yml.replace('04Source','Source')
yml = yml.replace('05Emplacement','Emplacement')
yml = yml.replace('06Poids','Poids')
yml = yml.replace('07Aura','Aura')
yml = yml.replace('08NLS','NLS')
yml = yml.replace('09Conditions','Conditions')
yml = yml.replace('10Coût','Coût')
yml = yml.replace('20Description','Description')
yml = yml.replace('21Référence','Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)

