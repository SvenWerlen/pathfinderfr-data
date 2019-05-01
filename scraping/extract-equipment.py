#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html


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

MOCK_E = None
#MOCK_E = "mocks/materiel-aventurier.html"           # décommenter pour tester avec données pré-téléchargées


#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = content.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings

liste = []

# itération sur chaque page
for data in URLs:

    if MOCK_E:
        content = BeautifulSoup(open(MOCK_E),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(data["URL"]).read(),features="lxml").body

    tables = content.find_all('table',{'class':'tablo'})

    equipment = {'99Complete': False}
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
                    equipment['01Nom'] = cols[0].text.strip()
                    equipment[u'20Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
                else:
                    equipment['01Nom'] = cols[0].text.strip()
                    equipment[u'20Référence'] = data["URL"]

                if not cols[1].text.strip() and not cols[2].text.strip():
                    parent = {'01Nom':equipment['01Nom'], u'20Référence': equipment[u'20Référence']}
                    continue
                elif cols[0].text.startswith(' ') and parent:
                    equipment['01Nom'] = parent['01Nom'] + " (" + equipment['01Nom'].lower() + ")"
                    equipment[u'20Référence'] = parent[u'20Référence']
                elif cols[0].text.startswith(' ') and not parent:
                    print("SOMETHING STRANGE!!")
                    exit(1)
                else:
                    parent = None

                # Others
                equipment['01Nom'] = equipment['01Nom'].replace('’','\'')
                equipment['04Prix'] = cols[1].text.strip()
                equipment[u'10Catégorie'] = data["category"]
                equipment[u'09Poids'] = cols[2].text.strip().replace("kg1","kg")

                # Special for "Substances"
                if len(cols) == 4:
                    try:
                        equipment['10Artisanat'] = int(cols[3].text.strip())
                    except:
                        pass

                equipment['02Source'] = "MJ"
                equipment['EMPTY'] = ""
                liste.append(equipment)
                equipment = {'99Complete': False}


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
            names = [u"Menottes",u"Menottes de qualité supérieure".lower()]

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
            if l['01Nom'].lower() in names or l['01Nom'].lower().startswith(name.lower()):
                l[u'99Complete'] = True
                l[u'12Description'] = descr.strip()
                if not source is None:
                    l['02Source'] = source
                found = True
        if not found:
            print("COULD NOT FIND : '" + name + "'");


    section = jumpTo(html, 'h2',{'class':'separator'}, u"Descriptions")
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
                name = e.text.replace("¶","").strip()
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
    if  u'99Complete' in l and not l[u'99Complete']:
        print("INCOMPLETE: '" + l['01Nom'] + "'");
    del l[u'99Complete']


yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace('01Nom','Nom')
yml = yml.replace('02Source','Source')
yml = yml.replace('04Prix','Prix')
yml = yml.replace('09Poids','Poids')
yml = yml.replace('10Artisanat','Artisanat')
yml = yml.replace(u'10Catégorie',u'Catégorie')
yml = yml.replace(u'12Description',u'Description')
yml = yml.replace(u'20Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
