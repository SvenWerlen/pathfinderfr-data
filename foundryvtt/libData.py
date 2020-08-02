#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import re
import json
from jsonmerge import merge


def convertToLb(value):
  return round((value * 2.2) * 100) / 100;

##
## cette fonction tente de convertir un poids exprimé en texte en valeur (float)
##
def getWeight(weight):
  weight = weight.replace(",",".")
  
  try :  
    return float(weight) 
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
##
def mergeWithLetContribute(list, filepath):
  retlist = []
  lcList = json.load(open(filepath, 'r'))
  for el in list:
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
