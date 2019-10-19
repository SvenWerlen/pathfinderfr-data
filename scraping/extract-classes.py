#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html
import re

from libhtml import jumpTo, findAfter, findProperty, mergeYAML

## Configurations pour le lancement
MOCK_CLASS = None
#MOCK_CLASS = "mocks/classe-alchimiste.html"       # décommenter pour tester avec une classe pré-téléchargée
#MOCK_CLASS = "mocks/classe-antipaladin.html"       # décommenter pour tester avec une classe pré-téléchargée
#MOCK_CLASS = "mocks/classe-inquisiteur.html"       # décommenter pour tester avec une classe pré-téléchargée
#MOCK_CLASS = "mocks/classe-arpenteur.html"       # décommenter pour tester avec une classe pré-téléchargée

FIELDS = ['Nom', 'Prestige', 'CompétencesDeClasse', 'DésDeVie', 'Alignement', 'RangsParNiveau', 'Progression', 'Description', 'Source', 'Référence' ]
MATCH = ['Nom']


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

CONN = ('Connaissances (exploration souterraine)','Connaissances (folklore local)','Connaissances (géographie)','Connaissances (histoire)',
         'Connaissances (ingénierie)','Connaissances (mystères)','Connaissances (nature)','Connaissances (noblesse)','Connaissances (plans)','Connaissances (religion)');

#
# cette fonction convertit le nom 'Le barbare' => 'Barbare'
#
def extractName(name):
    idx = name.find("(")
    if idx > 0:
        name = name[0:idx-1]
    if name.lower().startswith(u"le ") or name.lower().startswith(u"la "):
        name = name[3:]
    elif name.lower().startswith(u"l'"):
        name = name[2:]
    return name[:1].upper() + name[1:].lower()

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
    name = extractName(content.find('h1', {"class": ["pagetitle"]}).string.strip())
    cl['Nom'] = name

    # référence
    cl['Référence'] = link
    
    # prestige
    if 'prestige' in data.keys() and data['prestige']:
        cl['Prestige'] = True
    
    # source
    cl['Source'] = data['source']

    # description
    descr = findAfter(content, "div", {"class": "presentation"},'i');
    cl['Description'] = descr

    # alignement
    align = findProperty(content.find(id='PageContentDiv'), "alignement");
    cl['Alignement'] = align

    # dés de vie
    desVie = findProperty(content.find(id='PageContentDiv'), "dés de vie");
    if desVie == None:
        desVie = findProperty(content.find(id='PageContentDiv'), "dé de vie");
    cl['DésDeVie'] = desVie
    
    # points de compétence
    LABELS = ["Points de compétence par niveau", "Rangs de compétence par niveau", "Points de compétence à chaque niveau", "Nombre de rangs par niveau"]
    ptsComp = None
    for L in LABELS:
        ptsComp = findProperty(content.find(id='PageContentDiv'), L);
        if ptsComp:
            break
    if not ptsComp:
        print("Points de compétence non-trouvé pour classe: %s" % name)
        exit(1)
    m = re.search('(\d) \\+ modificateur d[\'’]Intelligence', ptsComp)
    if not m:
        print("Points de compétence n'a pas pu être extrait!")
        exit(1)
    cl['RangsParNiveau'] = int(m.group(1))

    # compétences de classe
    cl['CompétencesDeClasse'] = []
    
    
    sectionNames = ["Compétences de classe", "Compétences de la classe"]
    section = None
    for s in sectionNames:
        section = jumpTo(content, 'h2',{'class':'separator'}, s)
        if section:
            break
    
    if not section:
        print("- Compétences de la classe %s n'a pas être trouvée!!!" % cl['Nom'])
        continue
    
    for s in section:
        if s.name == 'a' and (len(s.text) > 3 or s.text.lower() == "vol"):
            value = s.text
            if value == u"Connaissances":
                idx = s.next_sibling.index(')')
                if idx > 0:
                    value += s.next_sibling[0:idx+1].lower()
            
            value = value.replace('’',"'")
            # hacks
            if value == 'Utilisation des objets magiques':
                value = 'Utilisation d\'objets magiques'
            elif value == 'Connaissances (mystère)':
                value = 'Connaissances (mystères)'
        
            if value == 'Connaissances (toutes)' or value == 'Connaissances (tous les domaines)' or value == 'Connaissances (au choix, chaque compétence devant être prise séparément)':
                for c in CONN:
                    cl['CompétencesDeClasse'].append({'Compétence':c})
            else:
                cl['CompétencesDeClasse'].append({'Compétence':value.strip()})
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

    cl['Progression'] = []
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
            cl['Progression'].append({
                'Niveau': int(values[0]),
                'BBA': values[1],
                'Réflexes': values[2],
                'Vigueur': values[3],
                'Volonté': values[4],
                'SortMax': spellLvl,
            });

    # ajouter classe
    liste.append(cl)
    
    if MOCK_CLASS:
        break

print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/classes.yml", MATCH, FIELDS, HEADER, liste)
