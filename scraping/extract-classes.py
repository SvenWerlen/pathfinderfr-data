#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html


## Configurations pour le lancement
MOCK_CLASS = None
#MOCK_CLASS = "mocks/classe-alchimiste.html"       # décommenter pour tester avec une classe pré-téléchargée
#MOCK_CLASS = "mocks/classe-antipaladin.html"       # décommenter pour tester avec une classe pré-téléchargée

URLs = [
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Alchimiste.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Antipaladin.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chevalier.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Conjurateur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Inquisiteur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Oracle.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Sorci%c3%a8re.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Magus.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ninja.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Pistolier.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Samoura%c3%af.ashx", 'source': 'MJRA'},
    
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Arcaniste.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Bretteur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chaman.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chasseur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Enqu%c3%aateur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Lutteur.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Pr%c3%aatre%20combattant.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Sanguin.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Scalde.ashx", 'source': 'MJRA'},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tueur.ashx", 'source': 'MJRA'},    
]

PROPERTIES = [ u"Caractéristique associée", u"caractéristique associée", u"Formation nécessaire", u"Formation nécesssaire", u"Malus d’armure"]

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)


#
# cette fonction convertit le nom 'Le barbare' => 'Barbare'
#
def cleanName(name):
    if name.lower().startswith(u"le ") or name.lower().startswith(u"l' "):
        name = name[3:]
    return name[:1].upper() + name[1:].lower()

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
            return el.next_sibling.replace('.','').strip()
    return None

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
    cl = {}
    
    link = data['link']
    
    print("Processing %s" % link)
    pageURL = link
    
    if MOCK_CLASS:
        content = BeautifulSoup(open(MOCK_CLASS),features="lxml").body
    else:
        content = BeautifulSoup(urllib.request.urlopen(pageURL).read(),features="lxml").body

    # titre
    name = cleanName(content.find_next('caption').string.strip())
    cl[u'Nom'] = name

    # référence
    cl[u'Référence'] = link
    
    # source
    cl[u'Source'] = data['source']

    # description
    descr = findAfter(content, "div", {"class": "presentation"},'i');
    cl[u'Description'] = descr

    # alignement
    align = findProperty(content.find(id='PageContentDiv'), u"alignement");
    cl[u'Alignement'] = align

    # dés de vie
    desVie = findProperty(content.find(id='PageContentDiv'), u"dés de vie");
    if desVie == None:
        desVie = findProperty(content.find(id='PageContentDiv'), u"dé de vie");
    cl[u'DésDeVie'] = desVie

    # compétences de classe
    cl[u'CompétencesDeClasse'] = []
    section = jumpTo(html, 'h2',{'class':'separator'}, u"Compétences de classe")
    for s in section:
        if s.name == 'a' and len(s.text) > 3:
            value = s.text
            if value == u"Connaissances":
                idx = s.next_sibling.index(')')
                if idx > 0:
                    value += s.next_sibling[0:idx+1]
            
            cl[u'CompétencesDeClasse'].append({u'Compétence':value.strip()})
        elif s.name == 'br':
            break;

    # tableau
    rows = content.find_next('table',{"class": "tablo"}).find_all('tr')
    cl[u'Progression'] = []
    for r in rows:
        # ignorer les en-têtes
        if r.has_attr('class') and (r['class'][0] == 'titre' or r['class'][0] == 'soustitre'):
            continue
        idx = 0
        values = {}
        for val in r.find_all('td'):
            values[idx] = val.text.strip()
            idx+=1
            if idx==5:
                break

        if len(values) == 5:
            cl[u'Progression'].append({
                u'Niveau': int(values[0]),
                u'BBA': values[1],
                u'Réflexes': values[2],
                u'Vigueur': values[3],
                u'Volonté': values[4]
            });

    # ajouter classe
    liste.append(cl)
    
    if MOCK_CLASS:
        break

if MOCK_CLASS:
    print(yaml.safe_dump(liste,default_flow_style=False, allow_unicode=True))
    exit(1)

with open("classes.yml", "w") as f:
    yaml.safe_dump(liste, f, default_flow_style=False, allow_unicode=True)
