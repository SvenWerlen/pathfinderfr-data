#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import yaml
import sys
import html
from bs4 import BeautifulSoup
from lxml import html
import re
import xml.etree.ElementTree as ET

from libwiki import parseWiki, parseData, parseNumber, setValue, extractNumberWithSpecial, cleanText
from libhtml import mergeYAML

PATH = "../../pf1-screwturnwiki/Pathfinder-RPG/"

FIELDS = ['Nom', 'FP', 'Environnements', 'PX', 
          'CA', 'PV', 'Réf', 'RéfSpécial', 'Vig', 'VigSpécial', 'Vol', 'VolSpécial', 
          'For', 'Dex', 'Con', 'Int', 'Sag', 'Cha', 'BBA', 'BMO', 'BMOSpécial', 'DMD', 'DMDSpécial',
          'Référence']
MATCH = ['Nom']

pages = os.listdir(PATH)

liste = []

for page in pages:
  
  # ignore file starting with "Temp"
  isTemp = re.search('^temp[ -]', page.lower())
  if isTemp:
    continue;  
  
  # read the content of the file
  with open(PATH + page, 'r') as f:
    content = f.read()
  
  # extract metadata & content
  data = content.split('\n---\n')
  if len(data) != 2:
    print("[W] Invalid data format in '%s' (%d)" % (page, len(data)));
    continue
  
  metadata = yaml.load(data[0])
    
  # only consider monsters
  if not 'Categories' in metadata or not "Monstre" in metadata['Categories']:
    continue
  
  content = BeautifulSoup(data[1], "lxml")
  
  # page could contain multiple tables
  tables = content.find_all('table', {"class": "Bestiaire"})
  for t in tables:
    
    # table could contain multiple sections (i.e. monsters)
    sect = t.find_all('div', {"class": "BD"})
    for s in sect:
      
      b = {} 
      b['Nom'] = metadata['Title']
      b['Référence'] = "https://www.pathfinder-fr.org/Wiki/" + metadata['Name'] + ".ashx"
      
      field = None
      try:
        PARTS = [ 'défense', 'attaque', 'caractéristiques', 'caractéristiques de base', 'statistiques', 'statistiques de base', 'capacités spéciales', 'écologie', 'pouvoirs spéciaux', 'construction', 'rituel', 'particularités' ]
        part = "general"
        
        rows = s.text.split('\n')
        for r in rows:
          data = parseWiki(r)
          
          if not data:
            continue
          
          # Titre & FP
          field = 'FP'
          if data['s'] == 'BDTitre' and len(data['data']) > 1:
            b['Nom'] = data['data'][0].strip()
            fp = re.search('FP (\d+/?\d?)', data['data'][1])
            if fp:
              setValue(b, 'FP', fp.group(1))
          
          # Sous-titres
          if data['s'] == 'BDSousTitre':
            if data['data'][0].strip().lower() in PARTS:
              part = data['data'][0].strip().lower()
              continue
            else:
              print("[E] Invalid subsection '%s' (%s)" % (data['data'][0], b['Nom']));
              exit(1)
          
          # Environnements
          field = 'env'
          if data['s'] == 'pucem':
            setValue(b, 'Environnements', data['data'])
          
          # Other data
          if data['s'] == 'BDTexte':
            data = parseData(data['data'][0])
            if len(data) == 0:
              continue
          
          ##
          ## GENERAL
          ##
          if part == "general":
            
            field = 'px'
            if 'px' in data:
              setValue(b, 'PX', parseNumber(data['px'].replace("px","")))
            if 'xp' in data:
              setValue(b, 'PX', parseNumber(data['xp'].replace("xp","")))
            
            field = 'FP'
            if 'fp' in data:
              setValue(b, 'FP', parseNumber(data['fp']))
          
          ##
          ## DÉFENSE
          ##
          elif part == "défense":
            field = 'CA'
            if 'ca' in data:
              ca = data['ca']
              # Variant 1 (isolated)
              if ca.find('contact') < 0:
                setValue(b, 'CA', { 'valeur' : parseNumber(ca) })
              # Variant 2: CA 17, contact 9, pris au dépourvu 17 (naturelle +8, taille -1) 
              else:
                el = re.search("(\d+).*contact +(\d+).*dépourvu +(\d+).*\((.*)\)", ca)
                if el:
                  setValue(b, 'CA', { 'valeur' : parseNumber(el.group(1)), 'contact': parseNumber(el.group(2)), 'dépourvu': parseNumber(el.group(3)), 'calcul': el.group(4).strip() });
            # Variant 1 (isolated)
            if 'contact' in data:
              setValue(b['CA'], 'contact', parseNumber(data['contact']) )
            if 'pris au dépourvu' in data:
              el = re.search("(\d+).*\((.*)\)", data['pris au dépourvu'].strip())
              if el:
                setValue(b['CA'], 'dépourvu', parseNumber(el.group(1)))
                setValue(b['CA'], 'calcul', el.group(2).strip())
            
            field = 'pv'
            if 'pv' in data:
              parts = data['pv'].split(';')
              el = re.search("(\d+).+\((.*)\)", parts[0])
              if el:
                setValue(b, 'PV', { 'valeur' : parseNumber(el.group(1)), 'calcul' : cleanText(el.group(2)) });
              else:
                print("[E] Invalid PV format '%s' (%s)" % (parts[0], b['Nom']));
              #print(data['pv'])
            
            
            field = 'Réf'
            if 'réf' in data:
              num = extractNumberWithSpecial(data['réf'])
              setValue(b, 'Réf', num['num'])
              if 'special' in num:
                setValue(b, 'RéfSpécial', num['special'])
            field = 'Vig'
            if 'vig' in data:
              num = extractNumberWithSpecial(data['vig'])
              setValue(b, 'Vig', num['num'])
              if 'special' in num:
                setValue(b, 'VigSpécial', num['special'])
            field = 'Vol'
            if 'vol' in data:
              num = extractNumberWithSpecial(data['vol'])
              setValue(b, 'Vol', num['num'])
              if 'special' in num:
                setValue(b, 'VolSpécial', num['special'])
            
            
          
          ##
          ## ATTAQUE
          ##
          elif part == "attaque":
            # nothing
            bob = 1
          
          ##
          ## CARACTÉRISTIQUES
          ##
          elif part == "caractéristiques":
            field = 'for'
            if 'for' in data:
              setValue(b, 'For', parseNumber(data['for']))
            field = 'dex'
            if 'dex' in data:
              setValue(b, 'Dex', parseNumber(data['dex']))
            field = 'con'
            if 'con' in data:
              setValue(b, 'Con', parseNumber(data['con']))
            field = 'int'
            if 'int' in data:
              setValue(b, 'Int', parseNumber(data['int']))
            field = 'sag'
            if 'sag' in data:
              setValue(b, 'Sag', parseNumber(data['sag']))
            field = 'cha'
            if 'cha' in data:
              setValue(b, 'Cha', parseNumber(data['cha']))  
            
            field = 'BBA'
            if 'bba' in data:
              setValue(b, 'BBA', parseNumber(data['bba']))  
            field = 'BMO'
            if 'bmo' in data:
              num = extractNumberWithSpecial(data['bmo'])
              setValue(b, 'BMO', num['num'])
              if 'special' in num:
                setValue(b, 'BMOSpécial', num['special'])  
            field = 'DMD'
            if 'dmd' in data:
              num = extractNumberWithSpecial(data['dmd'])
              setValue(b, 'DMD', num['num'])
              if 'special' in num:
                setValue(b, 'DMDSpécial', num['special'])
            
            
          #field = 'CA'
          #if 'ca' in data:
          # setValue(b, 'CA', parseNumber(data['ca']))
          


      except Exception as e:
        print("Exception: %s (%s) - %s" % (b['Nom'], field, str(e)))
        #raise e
    
      # vérifier tous les champs
      isValid = True
      #for field in {'Nom', 'FP', 'PX', 'For', 'Dex', 'Con', 'Int', 'Sag', 'Cha', 'Référence'}:
      #  if field not in b:
      #    print("[W] Incomplete field '%s' for: %s\n%s" % (field, b['Nom'], b));
      #    isValid = False
      #    break
          
      if isValid:
        liste.append(b)
      #break  

  
print("Fusion avec fichier YAML existant...")

HEADER = ""

mergeYAML("../data/bestiaire.yml", MATCH, FIELDS, HEADER, liste)
