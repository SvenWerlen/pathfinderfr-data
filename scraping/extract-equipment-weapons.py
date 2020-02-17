#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import extractSource, jumpTo, cleanSectionName, mergeYAML

## Configurations pour le lancement
URLS = [ "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%c3%a9capitulatif%20des%20armes.ashx",
        "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tableau%20r%C3%A9capitulatif%20des%20armes%20orientales.ashx" ]
URLDETS = [ "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Descriptions%20individuelles%20des%20armes.ashx",
            "https://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Description%20des%20armes%20orientales.ashx" ]
MOCK_W = None
#MOCK_W = "mocks/weapons.html"           # décommenter pour tester avec les armes pré-téléchargées
MOCK_WD = None
#MOCK_WD = "mocks/weapons-details.html"  # décommenter pour tester avec les armes pré-téléchargées


FIELDS = ['Nom', 'Catégorie', 'Sous-catégorie', 'Source', 'Prix', 'DégâtsP', 'DégâtsM', 'Critique', 'Portée', 'Poids', 'Type', 'Spécial', 'Description', 'Référence' ]
MATCH = ['Nom']


liste = []

for URL in URLS:
    if MOCK_W:
        content = BeautifulSoup(open(MOCK_W),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(URL).read(),features="lxml").body

    sections = content.find_all('h2',{'class':'separator'})

    type1 = []

    # extraction des types
    for s in sections:
        if s.text.startswith("Accès rapide"):
            continue
        section = cleanSectionName(s.text)
        section = section.replace("Les armes", "Arme").replace("s","")
        type1.append(section)

    tables = content.find_all('table',{'class':'tablo'})

    weapon = {}
    type2 = ""

    print("Extraction des armes...")

    idx = 0
    for t in tables:
        rows = t.find_all('tr')
        for r in rows:
            cols = r.find_all('td')
            if 'class' in r.attrs and 'titre' in r.attrs['class']:
                continue
            if len(cols) == 1 and 'class' in r.attrs and 'premier' in r.attrs['class']:
                type2 = r.text.strip()
                type2 = type2[0].upper() + type2[1:].lower()
                type2 = type2.replace('Armes','Arme')
                print("Extraction %s ..." % type2)
                continue
            if len(cols) == 9:
                # Name & Reference
                nameLink = cols[0].find('a')
                weapon['Nom'] = cols[0].text.strip()
                if weapon['Nom'].endswith(" (3)"):
                    weapon['Nom'] = weapon['Nom'][:-4]
                if not nameLink is None:
                    weapon['Référence'] = "http://www.pathfinder-fr.org/Wiki/" + nameLink['href']
                else:
                    weapon['Référence'] = URL
                # Others
                weapon['Nom'] = weapon['Nom'].replace('’','\'')
                weapon['Catégorie'] = type1[idx]
                weapon['Sous-catégorie'] = type2
                weapon['Prix'] = cols[1].text.strip()
                weapon['DégâtsP'] = cols[2].text.strip()
                weapon['DégâtsM'] = cols[3].text.strip()
                weapon['Critique'] = cols[4].text.strip()
                weapon['Portée'] = cols[5].text.strip()
                weapon['Poids'] = cols[6].text.strip()
                weapon['Type'] = cols[7].text.strip()
                weapon['Spécial'] = cols[8].text.strip()
                weapon['Complete'] = False

                weapon['Source'] = "MJ"
                liste.append(weapon)
                weapon = {}
        
        idx+=1


#
# cette fonction ajoute les infos additionelles
#
def addInfos(liste, name, source):
    names = []
    # ugly fix
    name = name.replace('’','\'')
    if(name == u"Coup-de-poing"):
        names = [u"Coup-de-poing américain".lower()]
    elif(name == u"Arbalète à répétition"):
        names = [u"Arbalète légère à répétition".lower(),u"Arbalète lourde à répétition".lower()]
    elif(name == u"Arbalète double ou Double arbalète"):
        names = [u"Arbalète double".lower()]
    elif(name == u"Masse d'armes"):
        names = [u"Masse d'armes lourde".lower(),u"Masse d'armes légère".lower()]
    elif(name == u"Flèche de fumée ou flèche fumigène"):
        names = [u"Flèches de fumée (20)".lower()]
    elif(name == u"Flèches assommantes ou flèches à têtes rondes"):
        names = [u"Flèches à tête ronde (20)".lower()]
    elif(name == u"Fléchette ou dard"):
        names = [u"Fléchettes".lower()]
    elif(name == u"Bille de fronde"):
        names = [u"Billes (10)".lower()]
    elif(name == u"Carreau d'arbalète"):
        names = [u"Carreaux (10)".lower()]
    elif(name == u"Flèches"):
        names = [u"Flèches (20)".lower()]
    elif(name == u"Flèches de vol"):
        names = [u"Flèches de vol (20)".lower()]
    elif(name == u"Shuriken"):
        names = [u"Shuriken (5)".lower()]
    elif(name == u"Fléchettes de sarbacane"):
        names = [u"Dard, sarbacane (10)".lower()]
    elif(name == u"Double lame ou épée double"):
        names = [u"Double-lame".lower()]
    elif(name == u"Rondache ou écu à pointes"):
        names = [u"Rondache à pointes".lower(),u"Rondache".lower(),u"Écu à pointes".lower()]
    elif(name == u"Arc composite"):
        names = [u"Arc court composite".lower(),u"Arc long composite".lower()]
    elif(name == u"Haches d'armes naine"):
        names = [u"Hache de guerre naine".lower()]
    elif(name == u"Bâton de jet halfelin ou fustibale halfelin"):
        names = [u"Bâton de jet halfelin".lower()]
    elif(name == u"Bolas bohémiens ou tribaux"):
        names = [u"Bolas tribaux".lower()]
    elif(name == u"Fléchettes wushu"):
        names = [u"Fléchettes wushu (5)".lower()]
    elif(name == u"Lungchuan tamo (dagues cachées)"):
        names = [u"Lungchuan tamo".lower()]
    elif(name == u"Épée à trois pointes et double tranchant"):
        names = [u"Épée à triple pointe et double tranchant".lower()]
    elif(name == u"Sansetsukon (bâton en trois parties)"):
        names = [u"Sansetsukon".lower()]
    elif(name == u"Lance-flèche"):
        names = [u"Tube à flèches".lower()]
    elif(name == u"Flèches de longue distance à tête de fer"):
        names = [u"Flèches de longue distance à tête de fer (20)".lower()]
    elif(name == u"Flèches sifflantes"):
        names = [u"Flèches sifflantes (20)".lower()]
    elif(name == u"Tube de sable empoisonné"):
        names = [u"Sable empoisonné".lower()]
    elif(name == u"Tekko-kagi"):
        names = [u"Tekko-kagi (griffe de fer)".lower()]
    elif(name == u"Kusarigama"):
        names = [u"Kusarigama (kama et chaîne)".lower()]
    else:
        names = [name.lower()]

    # add infos to existing weapon in list
    found = False
    for l in liste:
        if l['Nom'].lower() in names:
            l['Complete'] = True
            l['Description'] = descr.strip()
            if not source is None:
                l['Source'] = source
            found = True
    #if not found:
    #    print("- une description existe pour '" + name + "' mais pas le sommaire!");


for URLDET in URLDETS:

    if MOCK_WD:
        content = BeautifulSoup(open(MOCK_WD),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(URLDET).read(),features="lxml").body

    section = jumpTo(content, 'h1',{'class':'separator'}, u"À mains nues")
    if not section: 
        section = jumpTo(content, 'h1',{'class':'separator'}, u"Description individuelle des armes orientales")
        
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
                    else:
                        name = e.text.strip()
                        if name.endswith('.'):
                            name = name[:-1].strip()
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
                    sourceFound = extractSource(e)
                    if sourceFound:
                        source = sourceFound

    addInfos(liste, name, sourceNext)


for l in liste:
    if not l['Complete']:
        print("- aucune description n'existe pour '" + l['Nom'] + "'!");
    del l['Complete']


print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/armes.yml", MATCH, FIELDS, HEADER, liste)
