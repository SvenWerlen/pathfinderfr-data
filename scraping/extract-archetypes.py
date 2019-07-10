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
MOCK_ARCHLIST = None
MOCK_ARCHLIST = "mocks/archetypes.html"             # décommenter pour tester avec archetypes pré-téléchargés
MOCK_ARCH = None
#MOCK_ARCH = u"mocks/archetype-barbare-balafré.html" # décommenter pour tester avec un archetype pré-téléchargé
#MOCK_ARCH = u"mocks/archetype-bretteur.html" # décommenter pour tester avec un archetype pré-téléchargé


#
# cette fonction extrait le texte du prochain élément après ...
#
def findAfter(html, afterTag, afterCond, searched):
    elements = html.find_next(afterTag, afterCond).next_siblings
    for el in elements:
        if el.name == searched:
            return el.text.strip()

#
# cette fonction extrait le texte pour une propriété <b>propriété</b> en prenant le texte qui suit
#
def findProperty(html, propName):
    for el in html:
        if el.name == 'b' and el.text.lower().startswith(propName.lower()):
            value = ""
            for e in el.next_siblings:
                if e.name == 'br':
                    break
                elif e.string:
                    value += e.string
                else:
                    value += e
            return value.replace('.','').strip()
    return None

#
# cette fonction permet de sauter à l'élément recherché et retourne les prochains éléments
#
def jumpTo(html, afterTag, afterCond, elementText):
    seps = content.find_all(afterTag, afterCond);
    for s in seps:
        if s.text.lower().strip().startswith(elementText.lower()):
            return s.next_siblings



classes = []
with open("../data/classes.yml", 'r') as stream:
    try:
        classes = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


liste = []
classfeatures = []

list = []
if MOCK_ARCHLIST:
    parsed_html = BeautifulSoup(open(MOCK_ARCHLIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('div', class_="presentation" )
else:
    list = []
    for u in URLs:
        parsed_html = BeautifulSoup(urllib.request.urlopen(u).read(),features="lxml")
        list += parsed_html.body.find(id='PageContentDiv').find_all('tr')


# itération sur chaque tableau
idx = 0
for el in list:
    
    idx += 1
    if idx > 2:
        continue
    
    title = el.find_all('h2', limit=1)[0]
    classe = None
    
    m = re.search(u"Les archétypes (?:de |d\')(.+?)¶", title.text)
    if m:
        classe = m.group(1)[0].upper() + m.group(1)[1:]
    else:
        print("Extraction du nom de classe impossible: %s" % title.text)
        exit(1)
    
    found = False
    for c in classes:
        if c['Nom'] == classe:
            print("Processing %s" % classe)
            found = True
        
    if not found:
        print("Classe %s non-trouvée!" % classe)
        exit(1)
    
    archetypes = el.find_all('li')
    for a in archetypes:
        pageURL = "http://www.pathfinder-fr.org/Wiki/" + a.find_next('a').get('href')
        m = re.search(u"(.*)\((.*)\)", a.text)
        if m:
            nom = m.group(1).strip()
            source = m.group(2)
        else:
            print("Extraction du nom de l'archetype impossible: %s" % a.text)
            continue
        
        if source == "classe de base" or "(classe de base)" in nom:
            continue
        elif source == "UC" or source == "AG" or source == "Ag":
            source = "AG" # Art de la guerre
        elif source == "AM" or source == "UM":
            source = "AM" # Art de la magie
        elif source == "APG" or source == "MJRA":
            source = "MJRA" # Manuel des joueurs - règles avancées
        elif source == "MR":
            source = "MR" # Manuel des races
        elif source == "MCA":
            source = "MCA" # Manuel du joueur - classes avancées
        elif source == "MJRA,AG,AM":
            continue ## cas spécial - doit être fait à la main
        elif source == "MC":
            continue ## ???
        elif source == "Famf" or source == "FF":
            source = "FF"
        elif source == "CM":
            source = "CM" # Codex Monstrueux
        elif source == "AO":
            source = "AO" # Aventures occultes
        else:
            print("Source invalide %s!" % source)
            exit(1)
        
        ## ugly hack for Samouraï
        if nom == "Le samouraï (classe alternative)":
            nom = "Lame sainte"
            source = "AG"
            pageURL = "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.lame%20sainte%20(chevalier).ashx"
        ## ignore antipaladin (already exists as class)
        elif nom == "Antipaladin":
            continue
        
        if MOCK_ARCH:
            content = BeautifulSoup(open(MOCK_ARCH),features="lxml").body.find(id='PageContentDiv')
        else:
            content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body.find(id='PageContentDiv')
        
        descr = ""
        for e in content.children:
            if e.name == "h2" or e.name == "h3":
                break
            elif e.name == "i":
                descr += e.text
            
            
        archetype = {}
        archetype[u'01Nom'] = nom
        archetype[u'02Classe'] = classe
        archetype[u'03Source'] = source
        archetype[u'04Description'] = descr.strip()
        archetype[u'06Référence'] = pageURL
        archetype['EMPTY'] = ""
        found = True
        
        liste.append(archetype)
    
        ## extract class features for archetypes
        classfeature = {'4Source':'MJ','5Niveau':1,'6Auto': True}
        newObj = False
        descr = ""
        
        for s in content.children:
            if s.name == 'h3':
                if newObj:
                    classfeature['2Classe'] = classe
                    classfeature['3Archétype'] = nom
                    classfeature['7Description'] = descr.strip()
                    classfeature['EMPTY'] = ""
                    
                     # extraire niveau
                    lvl = re.search('Au niveau (\d+)', descr)
                    if lvl:
                        classfeature['5Niveau'] = int(lvl.group(1))
                                        
                    classfeatures.append(classfeature)
                    classfeature = {'4Source':'MJ','5Niveau':1,'6Auto': True}
                    brCount = 0
                    
                descr = ""
                classfeature['1Nom'] = s.text.replace('¶','').strip()
                newObj = True
                
                for e in s.children:
                    if e.name == 'a':
                        classfeature[u'8Référence']=pageURL + e['href']
            elif s.name == 'br':
                descr += '\n'
            elif s.name is None or s.name == 'a' or s.name == 'i' or s.name == 'b':
                if s.string is None:
                    for s2 in s.children:
                        if s2.name is None or s2.name == 'a' or s2.name == 'b' or s2.name == 'i':
                            descr += s2.string
                else:
                    descr += s.string
            elif s.name == "ul":
                for s2 in s.find_all("li"):
                    descr += "\n\n" + s2.text
                    
            elif s.name == 'div':
                for s2 in s.children:
                    if s2.name is None or s2.name == 'a' or s2.name == 'b' or s2.name == 'i':
                        if not s2.string is None:
                            descr += s2.string

        ## last element
        classfeature['2Classe'] = classe
        classfeature['3Archétype'] = nom
        classfeature['7Description'] = descr.strip()
        classfeature['EMPTY'] = ""
        
         # extraire niveau
        lvl = re.search('Au niveau (\d+)', descr)
        if lvl:
            classfeature['5Niveau'] = int(lvl.group(1))
        
        classfeatures.append(classfeature)

        if MOCK_ARCH:
            break


yml = yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True)
yml = yml.replace(u'01Nom',u'Nom')
yml = yml.replace(u'02Classe',u'Classe')
yml = yml.replace(u'03Source',u'Source')
yml = yml.replace(u'04Description',u'Description')
yml = yml.replace(u'06Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
#print(yml)


print("\n\n\n\n\n\n")

yml = yaml.safe_dump(classfeatures,default_flow_style=False, allow_unicode=True)
yml = yml.replace(u'1Nom',u'Nom')
yml = yml.replace(u'2Classe',u'Classe')
yml = yml.replace(u'3Archétype',u'Archétype')
yml = yml.replace(u'4Source',u'Source')
yml = yml.replace(u'5Niveau',u'Niveau')
yml = yml.replace(u'6Auto',u'Auto')
yml = yml.replace(u'7Description',u'Description')
yml = yml.replace(u'8Référence',u'Référence')
yml = yml.replace("EMPTY: ''",'')
print(yml)
