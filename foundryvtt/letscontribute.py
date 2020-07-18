#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
import os

SERVER = "https://boisdechet.org/fvtt"
#SERVER = "http://127.0.0.1:5000"

if not "LC_LOGIN" in os.environ:
  print("LC_LOGIN environment variable must be set!")
  exit(1)
if not "LC_SECRET" in os.environ:
  print("LC_SECRET environment variable must be set!")
  exit(1)


def checkReturnCode(response, expectedCode, context):
  if response.status_code != expectedCode:
    print("[%s] Unexpected response %s" % (context, response.status_code))
    try:
      print(r.json())
    except:
      print("No detail")
    exit(1)

##
## LOGIN to get access token
##
login = os.environ['LC_LOGIN']
secret = os.environ['LC_SECRET']
#login = "Global admin"
#secret = "test"

r = requests.post("%s/login" % SERVER, json={"login": login, "secret": secret})
checkReturnCode(r, 201, "Login")

token = r.json()['access_token']
headers = { "Authorization": "Bearer %s" % token }

##
## LIST of accepted entries
##
r = requests.get("%s/items/accepted" % SERVER, headers=headers)
checkReturnCode(r, 200, "Accepted")


lists={}

list = r.json()
for el in list:
  compendium = el['compendium'].split('.')[1]
  if not compendium in lists:
    lists[compendium] = {}
    
  r = requests.get("%s/item/%s" % (SERVER, el['id']), headers=headers)
  checkReturnCode(r, 200, "Details")
  data = r.json()['data']
  
  # extract contentNotes and changes only
  content = {}
  hasContent = False
  if "contextNotes" in data and len(data["contextNotes"]) > 0:
    content["contextNotes"] = data["contextNotes"]
    hasContent = True
  if "changes" in data and len(data["changes"]) > 0:
    content["changes"] = data["changes"]
    hasContent = True
  
  if hasContent:
    lists[compendium][el['name']] = { 'data': content }


for category in lists:
  # écrire le résultat dans le fichier d'origine
  outFile = open("letscontribute/%s.json" % category, "w")
  outFile.write(json.dumps(lists[category], indent=3, sort_keys=True))

  
