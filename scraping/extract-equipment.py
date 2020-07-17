#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, cleanSectionName, extractSource, mergeYAML, removeParenthesis, html2text

## Configurations pour le lancement
URLs = [
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.%C3%89quipement%20daventurier.ashx", 'category': u"Équipement d'aventurier"},
    
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Trousses%20doutils%20et%20de%20comp%c3%a9tences.ashx", 'category': u"Trousses d’outils et de compétences"},
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.V%c3%aatements.ashx", 'category': u"Vêtements"}, 
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Nourriture%20et%20Boissons.ashx", 'category': u"Nourriture et Boissons"},
    
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Outils%20alchimiques.ashx", 'category': u"Outils alchimiques"},
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Rem%c3%a8des%20alchimiques.ashx", 'category': u"Remèdes alchimiques"},
    
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Animaux%2c%20montures%20et%20leur%20%c3%a9quipement.ashx", 'category': u"Animaux, montures et leur équipement"},
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Moyens%20de%20transport.ashx", 'category': u"Moyens de transport", 'Poids': False},
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.H%c3%a9bergement%20et%20services.ashx", 'category': u"Hébergement et services"},
    {'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Jeux.ashx", 'category': u"Jeux"},
    
    ## À FAIRE!
    ##{'URL': "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Armes%20alchimiques.ashx", 'category': u"Armes alchimiques"}, 
    ##https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.%c3%89quipements%20raciaux.ashx
    ##https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Mat%c3%a9riaux%20sp%c3%a9ciaux.ashx
    ##https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Poisons.ashx
    
    ## FAIT MANUELLEMENT
    ##https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Marchandises.ashx
]

FIELDS = ['Nom', 'Source', 'Prix', 'Poids', 'Artisanat', 'Catégorie', 'Description', 'DescriptionHTML', 'Référence' ]
MATCH = ['Nom']


MOCK_E = None
#MOCK_E = "mocks/materiel-aventurier.html"           # décommenter pour tester avec données pré-téléchargées


liste = []

print("Extraction de l'équipement...")

# itération sur chaque page
for data in URLs:

    if MOCK_E:
        content = BeautifulSoup(open(MOCK_E),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(data["URL"]).read(),features="lxml").body

    print(data["URL"])
    tables = content.find_all('table',{'class':'tablo'})

    equipment = {'Complete': False}
    parent = None

    for t in tables:
        if "ignore" in t.attrs['class']:
            continue;
      
        rows = t.find_all('tr')
        for r in rows:
            # ignore some rows
            if 'class' in r.attrs and 'titre' in r.attrs['class']:
                continue

            cols = r.find_all('td')
            if len(cols) >= 2:
                # Name & Reference
                nameLink = cols[0].find('a')
                if not nameLink is None:
                    equipment['Nom'] = html2text(cols[0]).strip()
                    equipment['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
                else:
                    equipment['Nom'] = html2text(cols[0]).strip()
                    equipment['Référence'] = data["URL"]

                if not cols[1].text.strip() and (len(cols) == 2 or not cols[2].text.strip()):
                    parent = {'Nom':equipment['Nom'], 'Référence': equipment['Référence']}
                    continue
                elif (cols[0].text.startswith(' ') or cols[0].text.startswith(' ')) and parent:
                    equipment['Nom'] = removeParenthesis(parent['Nom']) + " (" + equipment['Nom'].lower() + ")"
                    equipment['Référence'] = parent['Référence']
                elif cols[0].text.startswith(' ') and not parent:
                    print("Child without a parent??? %s" % cols[0].text)
                    exit(1)
                else:
                    parent = {'Nom':equipment['Nom'], 'Référence': equipment['Référence']}

                # Others
                equipment['Nom'] = equipment['Nom'].replace('’','\'')
                equipment['Prix'] = html2text(cols[1]).strip()
                equipment['Catégorie'] = data["category"]
                if len(cols) >= 3 and (not 'Poids' in data or data['Poids']):
                  equipment['Poids'] = html2text(cols[2]).strip()
                else:
                  equipment['Poids'] = "—"

                # Special for "Substances"
                if len(cols) == 4:
                    try:
                        equipment['Artisanat'] = int(html2text(cols[3]).strip())
                    except:
                        pass

                equipment['Source'] = "MJ"
                
                liste.append(equipment)
                equipment = {'Complete': False}


    #
    # cette fonction ajoute les infos additionelles
    #
    def addInfos(liste, name, descr, descrHTML, source):
        names = []
        # ugly fix
        name = name.replace('’','\'')
        if name == u"Blanchis pour arme":
            names = [u"Blanchis"]
            
        elif name == u"Péage de route ou de pont":
            names = [u"Péage (route ou pont)"]

        elif name == u"Vin":
            names = [u"Vin de table", "Bon vin"]

        elif name == u"Cheval":
            names = [u"Cheval",u"Poney"]
        elif name == "Mors et filet":
            names = ["Mors et brides"]
        elif name == "Rat-Ane":
            names = ["Rat-âne"]

        else:
            names = [name]

        # add infos to existing weapong in list
        found = False
        for l in liste:
            for n in names:
                if l['Nom'].lower() == n.lower() or l['Nom'].lower().startswith(n.lower() + " "):
                    l['Complete'] = True
                    l['Description'] = descr.strip()
                    l['DescriptionHTML'] = descrHTML
                    if not source is None:
                        l['Source'] = source
                    found = True
        if not found:
            print("- une description existe pour '" + name + "' mais pas le sommaire!");


    section = jumpTo(content, 'h2',{'class':'separator'}, u"Descriptions")
    if not section:
      section = jumpTo(content, 'h2',{'class':'separator'}, data["category"])
    if not section:
      print("No descriptions found for %s" % data["category"])
      exit(1)
    
    newObj = True
    name = ""
    descr = ""
    descrHTML = ""
    source = None
    sourceNext = None
    for e in section:
        if e.name == 'h3':
            if not newObj:
                addInfos(liste, name, descr, descrHTML, sourceNext)

            sourceNext = source
            if e.name == 'h3':
                name = cleanSectionName(e.text)
                descr = ""
                descrHTML = ""
                source = None
                newObj = False

        else:
            descr += html2text(e)
            descrHTML += html2text(e, True, 2)
            if e.name == 'div' or e.name == 'img':
                src = extractSource(e)
                if src:
                    source = src

    addInfos(liste, name, descr, descrHTML, sourceNext)


for l in liste:
    if  'Complete' in l and not l['Complete']:
        print("- aucune description n'existe pour '" + l['Nom'] + "'!");
    del l['Complete']


print("Fusion avec fichier YAML existant...")

HEADER = ""
mergeYAML("../data/equipement.yml", MATCH, FIELDS, HEADER, liste)
