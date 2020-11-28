#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import re
import json
import os

from jsonmerge import merge

def convertToLb(value):
  return round((value * 2) * 100) / 100;

##
## cette fonction tente de convertir un poids exprimé en texte en valeur (float)
##
def getWeight(weight):
  weight = weight.replace(",",".")
  
  try :  
    return convertToLb(float(weight))
  except : 
    # just ignore
    weight
  
  m = re.search('([\d\.]+?) kg', weight)
  if m:
      return convertToLb(float(m.group(1)))
  m = re.search('([\d\.]+?) g', weight)
  if m:
      return convertToLb(float(m.group(1))/1000)
  
  
  return None


##
## cette fonction tente de convertir un prix exprimé en texte en valeur (float)
##
def getPrice(price):
  price = price.replace(",",".")
  
  try :  
    return float(price) 
  except : 
    # just ignore
    price
  
  m = re.search('([\d ]+?) po', price.replace('.',''))
  if m:
      return int(m.group(1).replace(' ', ''))
  return None


##
## cette fonction tente d'extraire une quantité d'un titre (ex: Flèches (20))
## retourn [quantité, nom]. Ex: [20, "Flèches"]
##
def extractQuantity(name):
  m = re.search('(.*)\((\d+?)\)(.*)', name)
  if m:
      name = m.group(1) + m.group(3)
      return [int(m.group(2)), name.replace("  ", " ").strip()]
  return [1, name]

##
## cette fonction harmonise l'affichage des titres en mettant la première lettre en majuscule et le reste en minuscule
##
def cleanTitle(title):
  return title[0].upper() + title[1:]

##
## cette fonction fusionne une liste de données (JSON) avec un fichier de contribution
## elle examine également si un raccourci pour appliquer les effets doit être ajouté à la description
##
def mergeWithLetContribute(clist, filepath, ignoreDuplicates = True):
  # clean list from duplicates
  exist = {}
  noDupList = []
  for el in clist:
    if ignoreDuplicates and el['name'] in exist:
      print("Ignoring duplicate %s" % el['name'])
      continue
    exist[el['name']] = True
    noDupList.append(el)
  
  # adapt description
  EFFECTS = "letscontribute/effets.json"
  if os.path.isfile(EFFECTS) :
    data = json.load(open(EFFECTS, 'r'))
    type = clist[0]['type'] if 'type' in clist[0] else 'journal'
    if type in data:
      effects = data[type]
      for el in noDupList:
        if el['name'] in effects:
          effect = effects[el['name']]
          effectLvl = ""
          if isinstance(effect,list):
            effectLvl = " au " + str(effect[1])
            effect = effect[0]
          el['data']['description']['value'] += "@Macro[effet]{Appliquer \"" + el['name'] + "\"" + effectLvl + " }"    
  
  if not os.path.isfile(filepath) :
    return noDupList
  
  retlist = []
  lcList = json.load(open(filepath, 'r'))
  for el in noDupList:
    name = el['name']
    if name in lcList:
      retlist.append(merge(el, lcList[name]))
      #print("%s merged!" % name)
    else:
      retlist.append(el)
      
  return retlist

##
## cette fonction trouve la chaîne de charactère commune et se terminant par un espace
## (utilisée pour extraire le nom d'une aptitude qui se répète)
## 
def longestSubstring(str1, str2):
  idx = 0
  len1 = len(str1)
  for i in range(len1):
    if str1[i] == ' ':
      idx = i
    if i >= len(str2) or str1[i] != str2[i]:
      return str1[0:idx]
  return str1

##
## cette fonction insère des macros dans les descriptions pour les dés
##
def improveDescription(descr, name):
  descr =  re.sub('\d+d\d+( ?\+ ?\d+)?', "[[/r \g<0> #%s]]" % name, descr)
  return descr
