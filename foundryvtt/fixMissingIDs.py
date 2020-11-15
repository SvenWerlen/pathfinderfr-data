#!/usr/bin/python3
# -*- coding: utf-8 -*-

import uuid
import json

files = [ "classfeaturesfr.json", "featsfr.json", "magicfr.json", "racesfr.json", "traitsfr.json" ]

for f in files:
  filepath = "letscontribute/%s" % f
  data = json.load(open(filepath, 'r'))
  for key in data:
    if "data" in data[key] and "changes" in data[key]["data"]:
      changes = data[key]["data"]["changes"]
      for c in changes:
        if "operator" in c and c["operator"] == "+":
          c["operator"] = "add"
        if not "_id" in c:
          c["_id"] = uuid.uuid4().hex[:8]
  
  outFile = open(filepath, "w")
  outFile.write(json.dumps(data, indent=3, sort_keys=True))
