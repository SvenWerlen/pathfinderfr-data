#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import jumpTo, cleanSectionName, mergeYAML

## Configurations pour le lancement
URLs = [
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Mat%c3%a9riel%20daventurier.ashx", 'category': u"Matériel d'aventurier"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Substances%20et%20objets%20sp%c3%a9ciaux.ashx", 'category': u"Substances et objets spéciaux"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Mat%c3%a9riel%20de%20classes%20et%20de%20comp%c3%a9tences.ashx", 'category': u"Matériel de classes et de compétences"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.V%c3%aatements.ashx", 'category': u"Vêtements"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Nourriture%2c%20boisson%20et%20h%c3%a9bergement.ashx", 'category': u"Nourriture, boisson et hébergement"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Montures%20et%20harnachement.ashx", 'category': u"Montures et harnachement"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Moyens%20de%20transport.ashx", 'category': u"Moyens de transport"},
    {'URL': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Objets%20r%c3%a9cr%c3%a9atifs.ashx", 'category': u"Objets récréatifs"},
]

FIELDS = ['Nom', 'Source', 'Prix', 'Poids', 'Artisanat', 'Catégorie', 'Description', 'Référence' ]
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

    tables = content.find_all('table',{'class':'tablo'})

    equipment = {'Complete': False}
    parent = None

    for t in tables:
        rows = t.find_all('tr')
        for r in rows:
            # ignore some rows
            if 'class' in r.attrs and 'titre' in r.attrs['class']:
                continue

            cols = r.find_all('td')
            if len(cols) >= 3:
                # Hotfix for multiple tables (http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Montures%20et%20harnachement.ashx?NoRedirect=1&NS=Pathfinder-RPG)
                if cols[0].text.strip().startswith("12 m"):
                    break

                # Name & Reference
                nameLink = cols[0].find('a')
                if not nameLink is None:
                    equipment['Nom'] = cols[0].text.strip()
                    equipment['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
                else:
                    equipment['Nom'] = cols[0].text.strip()
                    equipment['Référence'] = data["URL"]

                if not cols[1].text.strip() and not cols[2].text.strip():
                    parent = {'Nom':equipment['Nom'], 'Référence': equipment['Référence']}
                    continue
                elif cols[0].text.startswith(' ') and parent:
                    equipment['Nom'] = parent['Nom'] + " (" + equipment['Nom'].lower() + ")"
                    equipment['Référence'] = parent['Référence']
                elif cols[0].text.startswith(' ') and not parent:
                    print("SOMETHING STRANGE!!")
                    exit(1)
                else:
                    parent = None

                # Others
                equipment['Nom'] = equipment['Nom'].replace('’','\'')
                equipment['Prix'] = cols[1].text.strip()
                equipment['Catégorie'] = data["category"]
                equipment['Poids'] = cols[2].text.strip().replace("kg1","kg")

                # Special for "Substances"
                if len(cols) == 4:
                    try:
                        equipment['Artisanat'] = int(cols[3].text.strip())
                    except:
                        pass

                equipment['Source'] = "MJ"
                liste.append(equipment)
                equipment = {'Complete': False}


    #
    # cette fonction ajoute les infos additionelles
    #
    def addInfos(liste, name, descr, source):
        names = []
        # ugly fix
        name = name.replace('’','\'')
        if name == u"Sifflet d'alerte":
            names = [u"Sifflet d'alarme (ou silencieux)".lower()]
        elif name == u"Etui à parchemins":
            names = [u"Étui à cartes ou à parchemins".lower()]
        elif name == u"Feuille de papier":
            names = [u"Feuille de papier".lower(),u"Papier".lower()]
        elif name == u"Papier de riz":
            names = [u"Feuille de papier de riz".lower()]
        elif name == u"Menottes et menottes de qualité supérieure":
            names = [u"Menottes".lower(),u"Menottes de qualité supérieure".lower()]

        elif name == u"Instrument de musique, courants ou de maître":
            names = [u"Instrument de musique courant".lower(),u"Instrument de musique de maître".lower()]
        elif name == u"Symbole sacré, en bois ou en argent":
            names = [u"Symbole sacré en argent".lower(),u"Symbole sacré en bois".lower()]

        elif name == u"Auberge":
            name = u"Séjour à l'auberge"

        elif name == u"Barde pour créature de taille M ou G":
            name = u"Barde"
        elif name == u"Bât":
            names = [u"Selle (bât)".lower()]
        elif name == u"Destrier":
            names = [u"Cheval (destrier léger)".lower(),u"Cheval (destrier lourd)".lower()]
        elif name == u"Selle d'équitation":
            names = [u"Selle (d'équitation)".lower()]
        elif name == u"Selle de guerre":
            names = [u"Selle (de guerre)".lower()]
        elif name == u"Selle spéciale":
            name = u"Selle, spéciale"

        else:
            names = [name.lower()]

        # add infos to existing weapong in list
        found = False
        for l in liste:
            if l['Nom'].lower() in names or l['Nom'].lower().startswith(name.lower()):
                l['Complete'] = True
                l['Description'] = descr.strip()
                if not source is None:
                    l['Source'] = source
                found = True
        if not found:
            print("- une description existe pour '" + name + "' mais pas le sommaire!");


    section = jumpTo(content, 'h2',{'class':'separator'}, u"Descriptions")
    newObj = True
    name = ""
    descr = ""
    source = None
    sourceNext = None
    for e in section:
        if e.name == 'h3':
            if not newObj:
                addInfos(liste, name, descr, sourceNext)

            sourceNext = source
            if e.name == 'h3':
                name = cleanSectionName(e.text)
                descr = ""
                source = None
                newObj = False

        elif e.name == 'br':
            descr += "\n"
        elif e.name is None or e.name == 'a':
            if e.string:
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

    addInfos(liste, name, descr, sourceNext)


for l in liste:
    if  'Complete' in l and not l['Complete']:
        print("- aucune description n'existe pour '" + l['Nom'] + "'!");
    del l['Complete']


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/equipement.yml", MATCH, FIELDS, HEADER, liste)
