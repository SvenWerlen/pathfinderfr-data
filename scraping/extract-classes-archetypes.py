#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
import re
from bs4 import BeautifulSoup
from lxml import html

from libhtml import cleanName, cleanSectionName, cleanDescription, html2text, getValidSource, extractLevel, mergeYAML

## Configurations pour le lancement
MOCK_ARCHLIST = None
#MOCK_ARCHLIST = "mocks/archetypes-test.html"             # décommenter pour tester avec archetypes pré-téléchargés
MOCK_ARCH = None
#MOCK_ARCH = "mocks/archetype-spirite-hanté.html"
#MOCK_ARCH = u"mocks/archetype-barbare-balafré.html" # décommenter pour tester avec un archetype pré-téléchargé
#MOCK_ARCH = u"mocks/archetype-bretteur.html" # décommenter pour tester avec un archetype pré-téléchargé
#MOCK_ARCH = u"mocks/archetype-ens-tatoué.html" # décommenter pour tester avec un archetype pré-téléchargé
#MOCK_ARC = "mocks/archetype-pilleur.html" # décommenter pour tester avec un archetype pré-téléchargé

FIELDS_ARCHETYPE = ['Nom', 'Classe', 'Source', 'Description', 'Référence' ]
MATCH_ARCHETYPE  = ['Référence']
FIELDS_CLASSFEATURES = ['Nom', 'Classe', 'Archétype', 'Prérequis', 'Source', 'Niveau', 'Auto', 'Description', 'Référence' ]
MATCH_CLASSFEATURES  = ['Nom','Classe', 'Archétype']


classes = []
with open("../data/classes.yml", 'r') as stream:
    try:
        classes = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


liste = []
classfeatures = []

print("Extraction des archétypes...")

list = []
if MOCK_ARCHLIST:
    parsed_html = BeautifulSoup(open(MOCK_ARCHLIST),features="lxml")
    list = parsed_html.body.find(id='PageContentDiv').find_all('div', class_="presentation" )
else:
    parsed_html = BeautifulSoup(urllib.request.urlopen("http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Les%20arch%C3%A9types%20de%20classes.ashx").read(),features="lxml")
    list += parsed_html.body.find(id='PageContentDiv').find_all('div', class_="presentation" )


# itération sur chaque tableau
idx = 0
for el in list:
    
    idx += 1
    #if idx != 35:
    #    continue
    
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
            print("Traitement de la classe %s..." % classe)
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
            nom = nom[0] + nom[1:]
            source = m.group(2)
        else:
            print("Extraction du nom de l'archetype impossible: %s" % a.text)
            continue
        
        if source == "classe de base" or "(classe de base)" in nom or "(classe alternative)" in nom:
            continue
        elif source == "MJRA,AG,AM":
            continue ## cas spécial - doit être fait à la main
        elif source == "MC":
            continue ## ???
        else:
            source = getValidSource(source)
        
        print("- Archétype %s..." % nom)
        
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
        
        ## page not found? ignore
        if not content:
            continue
        
        descr = ""
        for e in content.children:
            if e.name == "h2" or e.name == "h3":
                break
            elif e.name == "i":
                descr += e.text
            
        archetype = {}
        archetype['Nom'] = nom
        archetype['Classe'] = classe
        archetype['Source'] = source
        archetype['Description'] = descr.strip()
        archetype['Référence'] = pageURL
        found = True
        
        liste.append(archetype)
        
        ## extract class features for archetypes
        classfeature = {'Source':'MJ','Niveau':1,'Auto': True}
        newObj = False
        descr = ""
        
        for s in content.children:
            if s.name == 'h3':
                if newObj:
                    classfeature['Classe'] = classe
                    classfeature['Archétype'] = nom
                    classfeature['Source'] = source
                    classfeature['Description'] = cleanDescription(descr)
                    classfeature['Niveau'] = extractLevel(classfeature['Description'],30)
                    classfeatures.append(classfeature)
                    classfeature = {'Source':'MJ','Niveau':1,'Auto': True}
                    brCount = 0
                    
                descr = ""
                featureName = cleanSectionName(s.text)
                if featureName.endswith('.'):
                    featureName = featureName[:-1]
                classfeature['Nom'] = cleanName(featureName[0] + featureName[1:])
                newObj = True
                
                for e in s.children:
                    if e.name == 'a':
                        classfeature['Référence']=pageURL + e['href']
            else:
                descr += html2text(s)

        ## last element
        classfeature['Classe'] = classe
        classfeature['Archétype'] = nom
        classfeature['Source'] = source
        classfeature['Description'] = cleanDescription(descr)
        classfeature['Niveau'] = extractLevel(classfeature['Description'],30)
        
         # extraire niveau
        lvl = re.search('Au niveau (\d+)', descr)
        if lvl:
            classfeature['Niveau'] = int(lvl.group(1))
        
        classfeatures.append(classfeature)

        if MOCK_ARCH:
            print(classfeature)
            exit(1)

print("Fusion avec fichier YAML existant (archétypes)...")
HEADER = ""

mergeYAML("../data/class-archetypes.yml", MATCH_ARCHETYPE, FIELDS_ARCHETYPE, HEADER, liste)

print("Fusion avec fichier YAML existant (features)...")

mergeYAML("../data/classfeatures.yml", MATCH_CLASSFEATURES, FIELDS_CLASSFEATURES, HEADER, classfeatures)
