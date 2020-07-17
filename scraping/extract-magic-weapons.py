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
#MOCK_MAGIC = "mocks/magic-weapons.html"                  # décommenter pour tester avec les armes pré-téléchargées
MOCK_MAGIC_DETAILS = None
#MOCK_MAGIC_DETAILS = "mocks/magic-weapons-details.html"  # décommenter pour tester avec le détails des armes pré-téléchargées

FIELDS = ['Nom', 'Résumé', 'Restrictions', 'Prix', 'PrixModif', 'Aura', 'NLS', 'Source', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']

# Plus rapide de copier directement ici que d'essayer d'extraire
TEXTE1 = 'Une arme magique sert à atteindre plus souvent sa cible et à lui infliger plus de dommages. Les armes magiques sont dotées d’un bonus d’altération allant de +1 à +5, bonus qui s’ajoute aux jets d’attaque et de dégâts de leur utilisateur. Elles sont également toutes des armes de maître, mais le bonus que cette qualité leur fournit ne s’ajoute pas à leur bonus d’altération.'
TEXTE2 = 'On trouve deux catégories d’armes : celles de corps à corps et celles à distance (comprenant les armes de jet et les armes à projectiles). Certaines armes de corps à corps peuvent également être utilisées en tant qu’armes à distance. Dans ce cas, leur bonus d’altération compte, quel qu’en soit l’usage.'
TEXTE3 = 'Une arme peut, en plus de son bonus d’altération, posséder certaines propriétés. Celles-ci sont considérées comme un bonus supplémentaire pour ce qui est du prix de l’arme, mais elles ne modifient pas son bonus à l’attaque ou aux dégâts (sauf indication contraire). Aucune arme ne peut avoir un bonus total (bonus d’altération plus équivalences dues aux propriétés, y compris celles qui proviennent des aptitudes du personnage et des sorts) supérieur à +10. Toute arme ayant une propriété spéciale doit avoir au moins un bonus d’altération de +1.'


liste = []


REFERENCE = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Armes%20magiques.ashx"
REFERENCE_DETAILS = "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Descriptions%20individuelles%20des%20propri%c3%a9t%c3%a9s%20sp%c3%a9ciales%20des%20armes.ashx"

if MOCK_MAGIC:
    content = BeautifulSoup(open(MOCK_MAGIC),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE).read(),features="lxml").body


##
## BONUS D'ALTERATION
##
table = getTableWithCaption( content, "Prix des bonus d'altération des armes" )
if not table:
    print("Table des prix de bonus d'altération non-trouvée!!")
    exit(1)

notes = []

for tr in table.find_all('tr'):
    if 'class' in tr.attrs and "titre" in tr.attrs['class']:
        continue
    tds = tr.find_all('td')
    if len(tds) == 2:
        price = re.search('([\d ]+) po', html2text(tds[1]))
        if price:
            price = int(price.group(1).replace(' ', ''))
        else:
            print("Prix invalide: %s" % html2text(tds[1]))
            
        liste.append({
          "Nom": "Bonus d'alteration %s" % cleanName(html2text(tds[0])),
          "Résumé": "Bonus d'altération qui s’ajoute aux jets d’attaque et de dégâts",
          "Prix": price,
          "Source": "MJ",
          "Référence": "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Armes%20magiques.ashx#PRIXBONUSDALTERATION"
        })
    else:
        notes.append(html2text(tds[0]))

# ajout des descriptions
description = "%s\n\n%s\n\n%s" % (TEXTE1, TEXTE2, TEXTE3)
descriptionHTML = "<p>%s</p><p>%s</p><p>%s</p>" % (TEXTE1, TEXTE2, TEXTE3)
for n in notes:
    description += "\n\n%s" % n
    descriptionHTML += "<p><i>%s</i></p>" % n
for el in liste:
    el['Description'] = description
    el['DescriptionHTML'] = descriptionHTML


##
## PROPRIÉTÉS
##
TABLE_NAMES = ["Propriétés ajoutant un prix spécifique", "Propriétés ajoutant un bonus de +1", "Propriétés ajoutant un bonus de +2", "Propriétés ajoutant un bonus de +3", "Propriétés ajoutant un bonus de +4", "Propriétés ajoutant un bonus de +5"]
NOTE = "Appliquées sur des armes à projectiles, les propriétés marquées d’un astérisque (*) sont transmises aux munitions tirées avec."
existing = {}
for T in TABLE_NAMES:
    table = getTableWithCaption( content, T )
    if not table:
      print("Table '%s' non-trouvée!!" % T)
      exit(1)
    
    for tr in table.find_all('tr'):
        if 'class' in tr.attrs and "titre" in tr.attrs['class']:
            continue
          
        trs = tr.find_all('td')
        if len(trs) == 5:
            nom = cleanName(html2text(trs[0]))
            link = trs[0].find('a')['href']
            hasNote = False
            if nom.endswith("*"):
                nom = nom[:-1]
                hasNote = True
            description = "%s\n\n%s" % (html2text(trs[3]), NOTE) if hasNote else "%s" % html2text(trs[3])
            element = {
              "Nom": "Propriété: %s" % nom,
              "Restrictions": html2text(trs[2]),
              "PrixModif": html2text(trs[4]),
              "Source": getValidSource(trs[1].text),
              "Résumé": description,
              "Référence": "https://www.pathfinder-fr.org/Wiki/%s" % link if link else REFERENCE_DETAILS
            }
            liste.append(element)
            existing[nom.lower()] = element

if MOCK_MAGIC_DETAILS:
    content = BeautifulSoup(open(MOCK_MAGIC_DETAILS),features="lxml").body
else:
    content = BeautifulSoup(urllib.request.urlopen(REFERENCE_DETAILS).read(),features="lxml").body


##
## DETAILS DES ARMES
##
for boite in content.find_all('div',{'class':['BD']}):
            
    data = {**extractBD_Type2(boite)}
    if not data['nomAlt'].lower() in existing:
      print("Propriété sans correspondance sur la page sommaire: %s" % data['nomAlt'])
      continue
    
    element = existing[data['nomAlt'].lower()]
    element['Description'] = data['descr']
    element['DescriptionHTML'] = data['descrHTML']
    element["Aura"] = data["aura"]
    element["NLS"] = int(data["nls"])
        
    del(existing[data['nomAlt'].lower()])


if len(existing) > 0:
    print("Éléments sans détails")
    print(existing)
    exit(1)

#exit(1)

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/magic-armes.yml", MATCH, FIELDS, HEADER, liste)
