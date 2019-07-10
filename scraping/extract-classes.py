#!/usr/bin/python3
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
#MOCK_CLASS = "mocks/classe-inquisiteur.html"       # décommenter pour tester avec une classe pré-téléchargée
#MOCK_CLASS = "mocks/classe-arpenteur.html"       # décommenter pour tester avec une classe pré-téléchargée

URLs = [
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Barbare.ashx", 'source': 'MJ', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Barde.ashx", 'source': 'MJ', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Druide.ashx", 'source': 'MJ', 'spellLvl': 9, 'spellLvl0': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ensorceleur.ashx", 'source': 'MJ', 'spellLvl': 9},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Guerrier.ashx", 'source': 'MJ', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Magicien.ashx", 'source': 'MJ', 'spellLvl': 9, 'spellLvl0': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Moine.ashx", 'source': 'MJ', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Paladin.ashx", 'source': 'MJ', 'spellLvl': 4},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Pr%c3%aatre.ashx", 'source': 'MJ', 'spellLvl': 9, 'spellLvl0': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.R%c3%b4deur.ashx", 'source': 'MJ', 'spellLvl': 4},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Roublard.ashx", 'source': 'MJ', 'spellLvl': 0},

    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Alchimiste.ashx", 'source': 'MJRA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Antipaladin.ashx", 'source': 'MJRA', 'spellLvl': 4},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chevalier.ashx", 'source': 'MJRA', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Conjurateur.ashx", 'source': 'MJRA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Inquisiteur.ashx", 'source': 'MJRA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Oracle.ashx", 'source': 'MJRA', 'spellLvl': 9},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Sorci%c3%a8re.ashx", 'source': 'MJRA', 'spellLvl': 9, 'spellLvl0': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Magus.ashx", 'source': 'AM', 'spellLvl': 6, 'spellLvl0': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ninja.ashx", 'source': 'AG', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Pistolier.ashx", 'source': 'AG', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Samoura%c3%af.ashx", 'source': 'AG', 'spellLvl': 0},
    
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Arcaniste.ashx", 'source': 'MCA', 'spellLvl': 9},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Bretteur.ashx", 'source': 'MCA', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chaman.ashx", 'source': 'MCA', 'spellLvl': 9},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chasseur.ashx", 'source': 'MCA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Enqu%c3%aateur.ashx", 'source': 'MCA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Lutteur.ashx", 'source': 'MCA', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Pr%c3%aatre%20combattant.ashx", 'source': 'MCA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Sanguin.ashx", 'source': 'MCA', 'spellLvl': 4},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Scalde.ashx", 'source': 'MCA', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Tueur.ashx", 'source': 'MCA', 'spellLvl': 0},
    
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Cin%c3%a9tiste.ashx", 'source': 'AO', 'spellLvl': 0},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Hypnotiseur.ashx", 'source': 'AO', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.M%c3%a9dium.ashx", 'source': 'AO', 'spellLvl': 4},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Occultiste.ashx", 'source': 'AO', 'spellLvl': 6},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Psychiste.ashx", 'source': 'AO', 'spellLvl': 9},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Spirite.ashx", 'source': 'AO', 'spellLvl': 6},
    
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Archer-mage.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Arpenteur%20dhorizon.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Assassin.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Champion%20occultiste.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Chroniqueur.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Disciple%20draconien.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Duelliste.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Fid%c3%a8le%20d%c3%a9fenseur.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Gardien%20de%20la%20nature.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Gardien%20du%20savoir.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.H%c3%a9raut.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ma%c3%aetre%20chYmiste.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ma%c3%aetre%20des%20ombres.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Ma%c3%aetre%20espion.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Mystificateur%20profane.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Proph%c3%a8te%20enrag%c3%a9.ashx", 'source': 'MJRA', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Th%c3%a9urge%20mystique.ashx", 'source': 'MJ', 'prestige': True},
    {'link': "http://www.pathfinder-fr.org/Wiki/Pathfinder-RPG.Vengeur%20sacr%c3%a9.ashx", 'source': 'MJRA', 'prestige': True},
    
]

CONN = (u'Connaissances (exploration souterraine)',u'Connaissances (folklore local)',u'Connaissances (géographie)',u'Connaissances (histoire)',
         'Connaissances (ingénierie)',u'Connaissances (mystères)',u'Connaissances (nature)',u'Connaissances (noblesse)',u'Connaissances (plans)',u'Connaissances (religion)');

# vérification des paramètres
if len(sys.argv) < 1:
    print("Usage: %s" % sys.argv[0])
    exit(1)


#
# cette fonction convertit le nom 'Le barbare' => 'Barbare'
#
def cleanName(name):
    if name.lower().startswith(u"le ") or name.lower().startswith(u"la "):
        name = name[3:]
    elif name.lower().startswith(u"l'"):
        name = name[2:]
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
    
    # prestige
    if 'prestige' in data.keys() and data['prestige']:
        cl[u'Prestige'] = True
    
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
    if section is None:
        section = jumpTo(html, 'h2',{'class':'separator'}, u"Compétences de la classe")
    
    for s in section:
        if s.name == 'a' and len(s.text) > 3:
            value = s.text
            if value == u"Connaissances":
                idx = s.next_sibling.index(')')
                if idx > 0:
                    value += s.next_sibling[0:idx+1].lower()
            
            value = value.replace('’',"'")
            # hacks
            if value == u'Utilisation des objets magiques':
                value = u'Utilisation d\'objets magiques'
            elif value == u'Connaissances (mystère)':
                value = u'Connaissances (mystères)'
        
            if value == u'Connaissances (toutes)' or value == u'Connaissances (tous les domaines)' or value == u'Connaissances (au choix, chaque compétence devant être prise séparément)':
                for c in CONN:
                    cl[u'CompétencesDeClasse'].append({u'Compétence':c})
            else:
                cl[u'CompétencesDeClasse'].append({u'Compétence':value.strip()})
        elif s.name == 'br':
            break;

    # tableau (progression)
    rows = content.find_next('table',{"class": "tablo"}).find_all('tr')

    maxSpellLvl = 0;
    minSpellLvl = 1;
    if 'spellLvl' in data.keys():
        maxSpellLvl = data['spellLvl']
    if 'spellLvl0' in data.keys() and  data['spellLvl0']:
        minSpellLvl = 0

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

        spellLvl = 0
        if len(values) >= 6 + maxSpellLvl:
            spellLvl = maxSpellLvl
            for idx in range(minSpellLvl,maxSpellLvl+1):
                if(values[6+idx-minSpellLvl]=='-'):
                    spellLvl = idx - 1;
                    break;

        if len(values) >= 5:
            cl[u'Progression'].append({
                u'Niveau': int(values[0]),
                u'BBA': values[1],
                u'Réflexes': values[2],
                u'Vigueur': values[3],
                u'Volonté': values[4],
                u'SortMax': spellLvl,
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
