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
MOCK_MAGIC = None
#MOCK_MAGIC = "mocks/magic-objets.html"                  # décommenter pour tester avec les objets merveilleux pré-téléchargées
MOCK_MAGIC_ITEM = None
#MOCK_MAGIC_ITEM = "mocks/magic-ailes-vol.html"      # décommenter pour tester avec détails pré-téléchargé
#MOCK_MAGIC_ITEM = "mocks/magic-casque-comprehension.html"      # décommenter pour tester avec détails pré-téléchargé

MOCK_MAGIC_SPECIFIC = None

TEXTE = ''

FIELDS = ['Nom', 'Type', 'Prix', 'Source', 'Emplacement', 'Poids', 'Aura', 'NLS', 'Conditions', 'Coût', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']

liste = []


links = {
  'Objets merveilleux': { "liste": [] },
  'Armes magiques spécifiques': { "liste": [], "emplacement": "mains" },
  'Armures magiques spécifiques': { "liste": [], "emplacement": "armure" },
  'Boucliers magiques spécifiques': { "liste": [], "emplacement": "bouclier" },
}

liste = []


##
## OBJETS MERVEILLEUX (LIENS SEULEMENT)
##

print("Extraction des références (objets merveilleux)...")
PATHFINDER = "http://www.pathfinder-fr.org/Wiki/"
REFERENCE = PATHFINDER + "Pathfinder-RPG.Liste%20alphab%c3%a9tique%20des%20objets%20merveilleux.ashx"

if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body

multicol = content.find_all('div',{'class':['article_3col']})
for m in multicol:
    for link in m.find_all('a'):
        # extraire adresse URL
        reference = PATHFINDER + link['href']
                
        # skip unknown links
        if('class' in link.attrs and 'unknownlink' in link['class']):
            continue
        
        #links['Objets merveilleux']['liste'].append(reference)

print("- %d objects found" % len(links['Objets merveilleux']['liste']))

##
## ARMES, ARMURES ET BOUCLIERS SPÉCIFIQUES (LIENS SEULEMENT)
##

REFERENCES = {
  "Armes magiques spécifiques": "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Armes%20magiques%20sp%c3%a9cifiques.ashx",
  "Armures magiques spécifiques": "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.armures%20magiques%20sp%c3%a9cifiques.ashx",
  "Boucliers magiques spécifiques": "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.boucliers%20magiques%20sp%c3%a9cifiques.ashx"
}
  
for R in REFERENCES:
    print("Extraction des références (%s)..." % R)
    
    if MOCK_MAGIC_SPECIFIC:
        content = BeautifulSoup(open(MOCK_MAGIC_SPECIFIC),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(REFERENCES[R]).read(),features="lxml").body

    TABLE_NAMES = [R]
    for T in TABLE_NAMES:
        table = getTableWithCaption( content, T )
        if not table:
          print("Table '%s' non-trouvée!!" % T)
          exit(1)
        
        for tr in table.find_all('tr'):
            if 'class' in tr.attrs and "titre" in tr.attrs['class']:
                continue
              
            trs = tr.find_all('td')
            if len(trs) == 4:
                link = trs[0].find('a')
                if link:
                    links[R]['liste'].append(PATHFINDER + link['href'])
                    
    print("- %d objects found" % len(links[R]['liste']))   


for TYPE in links:
    print("Traitement de %s..." % TYPE)
    for reference in links[TYPE]['liste']:

        # débogage
        print("- %s" % reference)
        
        # récupérer le détail d'un objet
        if MOCK_MAGIC_ITEM:
            page = BeautifulSoup(open(MOCK_MAGIC_ITEM),features="lxml").body
        else:
            try:
                page = BeautifulSoup(urllib.request.urlopen(reference).read(),features="lxml").body
                
                pageNotFound = page.find('h1',{'class':['pagetitlesystem']})
                if(pageNotFound and pageNotFound.text() == 'Page Not Found'):
                    print("Page doesn't exist! Skipping...")
                    continue
                
            except:
                print("Page doesn't exist! Skipping...")
                continue

        for boite in page.find_all('div',{'class':['BD']}):
            
            data = {**extractBD_Type2(boite)}
            descr = data['descr']
            descrHTML = data['descrHTML']
            
            if len(data['descr']) == 0:
                print("Description invalide pour: %s" % href)
                exit(1)
            
            element = {}
            element["Nom"] = data["nomAlt"] # prendre le nom de la page détaillée
            element["Type"] = TYPE
            element["Prix"] = data["prixAlt"] # prendre le prix de la page détaillée
            element["Source"] = "MJ"
            element["Description"] = data["descr"]
            element["DescriptionHTML"] = data["descrHTML"]
            element["Référence"] = reference
            
            # infos additionnelles
            if "emplacement" in data:
                element["Emplacement"] = data["emplacement"]
            elif 'emplacement' in links[TYPE]:
                element["Emplacement"] = links[TYPE]['emplacement']
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
            
            # si l'objet à plusieurs prix, alors créer les variations de l'objet
            variations = re.split('(?<=\)),\s+|(?<=\))\s+ou\s+', element["Prix"]) 
            if len(variations) > 1:
                
                added = False
                for variation in variations:
                    varElement = dict(element)
                    try:
                        price = re.search('^(.+? po) \(', variation).group(1)
                    except:
                        print("ERROR: Could not extract the variation detail for " + element["Nom"] + " '" + variation + "'")
                        exit(1)
                    try:
                        detail = re.search('po \((.+?)\)$', variation).group(1)
                    except:
                        print("ERROR: Could not extract the variation detail for " + element["Nom"] + "'" + variation + "'")
                        exit(1)
                    varElement["Prix"] = price
                    varElement["Nom"] = element["Nom"] + " (" + detail + ")"
                    print("Creation de la variation " + varElement["Nom"])
                    liste.append(varElement)
                    
            else:
                liste.append(element)
                    
#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic.yml", MATCH, FIELDS, HEADER, liste)

