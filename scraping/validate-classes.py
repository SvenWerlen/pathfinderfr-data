#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import typing
import sys

# vérification des paramètres
if len(sys.argv) < 2:
    print("Usage: %s [CHEMIN]" % sys.argv[0])
    print(" - CHEMIN: chemin vers fichier YML des classes")
    exit(1)

data = None
with open(sys.argv[1], 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

COMPS = (u'Acrobaties',u'Art de la magie',u'Artisanat',u'Bluff',u'Connaissances (exploration souterraine)',u'Connaissances (folklore local)',u'Connaissances (géographie)',u'Connaissances (histoire)',
         'Connaissances (ingénierie)',u'Connaissances (mystères)',u'Connaissances (nature)',u'Connaissances (noblesse)',u'Connaissances (plans)',u'Connaissances (religion)',u'Déguisement',u'Diplomatie',
         'Discrétion',u'Dressage',u'Équitation',u'Escalade',u'Escamotage',u'Estimation',u'Évasion',u'Intimidation',u'Linguistique',u'Natation',u'Perception',u'Premiers secours',u'Profession',u'Psychologie',
         'Représentation',u'Sabotage',u'Survie',u'Utilisation d\'objets magiques',u'Vol');

for d in data:
    if d[u'Nom'] is None or len(d[u'Nom']) < 5:
        print(u"Nom de classe invalide: %s" % d[u'Nom'])
    if d[u'Source'] is None or d[u'Source'] not in ("MJ", "MJRA", "MCA", "MR", "B1", "AG", "AM", "AO", "CCMI", "PAIZO", "RTT", "PMI", "MMI", "FF", "CM", "AE", "MPNJ", "MM", "AA", "HOTS", "RSE", "UI", "UW", "WOV"): ## see libhtml.py
        print(u"Nom de source invalide: %s pour %s" % (d[u'Source'],d[u'Nom']))
    if d[u'Alignement'] is None or len(d[u'Alignement']) < 4:
        print(u"Alignement invalide: %s pour %s" % (d[u'Alignement'],d[u'Nom']))
    if d[u'DésDeVie'] is None or len(d[u'DésDeVie']) < 2:
        print(u"Alignement invalide: %s pour %s" % (d[u'Alignement'],d[u'Nom']))
    if d[u'Référence'] is None or (not d[u'Référence'].startswith('http://www.pathfinder-fr.org') and not d[u'Référence'].startswith('https://www.pathfinder-fr.org')):
        print(u"Référence invalide: %s pour %s" % (d[u'Référence'],d[u'Nom']))
    
    if not isinstance(d[u'CompétencesDeClasse'], typing.List):
        print(u"CompétencesDeClasse invalid pour: %s" % d[u'Nom'])
    
    if len(d[u'CompétencesDeClasse']) < 5 and d[u'Prestige'] is None:
        print(u"Nombre de compétences trop faible pour: %s" % d[u'Nom'])
    if len(d[u'CompétencesDeClasse']) < 3 and d[u'Prestige']:
        print(u"Nombre de compétences trop faible pour: %s" % d[u'Nom'])
    
    for c in d[u'CompétencesDeClasse']:
        if c[u'Compétence'] is None or c[u'Compétence'] not in COMPS:
            print(u"Compétence de classe invalide: %s pour %s" % (c[u'Compétence'],d[u'Nom']))
    
    #bba = 0
    niveau = 0
    vig = 0
    vol = 0
    ref = 0
    sortMax = 0
    for niv in d[u'Progression']:
        # vérifier niveaux
        if int(niv[u'Niveau']) != niveau + 1:
            print(u"Niveau invalide %s pour %s" % (niv[u'Niveau'],d[u'Nom']))
        niveau += 1
        # vig
        if(int(niv[u'Vigueur'])<vig):
            print(u"Vigueur invalide %s pour %s au niveau %s" % (niv[u'Vigueur'],d[u'Nom'],niv[u'Niveau']))
        vig = int(niv[u'Vigueur'])
        # vol
        if(int(niv[u'Volonté'])<vol):
            print(u"Volonté invalide %s pour %s au niveau %s" % (niv[u'Volonté'],d[u'Nom'],niv[u'Niveau']))
        vol = int(niv[u'Volonté'])
        # ref
        if(int(niv[u'Réflexes'])<ref):
            print(u"Réflexes invalide %s pour %s au niveau %s" % (niv[u'Réflexes'],d[u'Nom'],niv[u'Niveau']))
        ref = int(niv[u'Réflexes'])
        # sortMax
        if(int(niv[u'SortMax'])<sortMax):
            print(u"SortMax invalide %s pour %s au niveau %s" % (niv[u'SortMax'],d[u'Nom'],niv[u'Niveau']))
        sortMax = int(niv[u'SortMax'])

    prestige = False
    if 'Prestige' in d.keys():
        prestige = d[u'Prestige']

    if not prestige and niveau != 20 :
        print(u"Niveau s'arrête à %s pour %s" % (niveau,d[u'Nom']))
    elif prestige and niveau != 10 :
        print(u"Niveau s'arrête à %s pour %s" % (niveau,d[u'Nom']))
    
    #print("Processing %s" % d['Nom'])
    
