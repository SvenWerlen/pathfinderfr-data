#!/usr/bin/python3
# -*- coding: utf-8 -*-


# tables de correspondances
TARGETS = {
  "CA": { 'id': "ac", "subtargets": {
    "Générique": "ac",
    "Armure": "aac",
    "Bouclier": "sac",
    "Armure naturelle": "nac"
  }},
  "Jets d'attaque": { 'id': "attack", "subtargets": {
    "Tous": "attack",
    "Corps-à-corps": "mattack",
    "Distance": "rattack"
  }},
  "Dégâts": { 'id': "damage","subtargets": {
    "Tous": "damage",
    "Dégâts de l'arme": "wdamage",
    "Dégâts du sort": "sdamage"
  }},
  "Score de caractéristique": { 'id': "ability", "subtargets": {
    "Force": "str",
    "Dextérité": "dex",
    "Constitution": "con",
    "Intelligence": "int",
    "Sagesse": "wis",
    "Charisme": "cha"
  }},
  "Jets de sauvegarde": { 'id': "savingThrows", "subtargets": {
    "Tous": "allSavingThrows",
    "Vigueur": "ref",
    "Réflexes": "fort",
    "Volonté": "will"
  }},
  "Compétences": { 'id': "skills","subtargets": {
    "Toutes": "skills",
    "Basées sur la Force": "strSkills",
    "Basées sur la Dextérité": "dexSkills",
    "Basées sur la Constitution": "conSkills",
    "Basées sur l'Intelligence": "intSkills",
    "Basées sur la Sagesse": "wisSkills",
    "Basées sur le Charisme": "chaSkills"
  }},
  "Compétence spécifique": { 'id': "skill","subtargets": {
    "Acrobaties": "acr",
    "Art de la magie": "spl",
    "Artisanat": "crf",
    "Artistry": "art",
    "Bluff": "blf",
    "Connaissances (Exploration souterraine)": "kdu",
    "Connaissances (Folklore local)": "klo",
    "Connaissances (Géographie)": "kge",
    "Connaissances (Histoire)": "khi",
    "Connaissances (Ingénierie)": "ken",
    "Connaissances (Mystères)": "kar",
    "Connaissances (Nature)": "kna",
    "Connaissances (Noblesse)": "kno",
    "Connaissances (Plans)": "kpl",
    "Connaissances (Religion)": "kre",
    "Déguisement": "dis",
    "Diplomatie": "dip",
    "Discrétion": "ste",
    "Dressage": "han",
    "Équitation": "rid",
    "Escalade": "clm",
    "Escamotage": "slt",
    "Estimation": "apr",
    "Évasion": "esc",
    "Intimidation": "int",
    "Lore": "lor",
    "Linguistique": "lin",
    "Natation": "swm",
    "Perception": "per",
    "Premiers Secours": "hea",
    "Profession": "pro",
    "Psychologie": "sen",
    "Représentation": "prf",
    "Sabotage": "dev",
    "Survie": "sur",
    "Utilisation d'objets magiques": "umd",
    "Vol": "fly"
  }},
  "Tests de caractéristique": { 'id': "abilityChecks","subtargets": {
    "Tous": "allChecks",
    "Test de Force": "strChecks",
    "Test de Dextérité": "dexChecks",
    "Test de Constitution": "conChecks",
    "Test de Intelligence": "intChecks",
    "Test de Sagesse": "wisChecks",
    "Test de Charisme": "chaChecks"
  }},
  "Vitesse": { 'id': "speed", "subtargets": {
    "Toutes": "allSpeeds",
    "Vit. Base": "landSpeed",
    "Vit. Escalade": "climbSpeed",
    "Vit. Natation": "swimSpeed",
    "Vit. Creuser": "burrowSpeed",
    "Vit. Vol": "flySpeed"
  }},
  "Div.": { 'id': "misc", "subtargets": {
    "BBA": "cmb",
    "DMD": "cmd",
    "Initiative": "init",
    "Points de vie": "mhp",
    "Blessure": "wounds",
    "Vigueur": "vigor"
  }}
}

TYPES = {
  "Non-typé": "untyped",
  "Alchimique": "alchemical",
  "Altération": "enh",
  "Altération à l'armure": "enh",
  "Altération à l'armure naturelle": "enh",
  "Altération au bouclier": "enh",
  "Aptitude": "competence",
  "Armure": "base",
  "Armure naturelle": "base",
  "Bouclier": "base",
  "Chance": "luck",
  "Esquive": "dodge",
  "Inné": "inherent",
  "Intuition": "insight",
  "Moral": "morale",
  "Parade": "deflection",
  "Résistance": "resist",
  "Taille": "size"
}


#
# cette fonction crée un nouveau "buff" basé sur la structure de pf1
#
def createChange(formula, target, subtarget, type):
  if not target in TARGETS:
    print("Invalid target '%s'" % target)
    exit(1)
  target = TARGETS[target]
  
  if not subtarget in target["subtargets"]:
    print("Invalid subtarget '%s'" % subtarget)
    exit(1)
  subtarget = target["subtargets"][subtarget]
  
  if not type in TYPES:
    print("Invalid bonus type '%s'" % type)
    exit(1)
  type = TYPES[type]
  
  changes = {
    'formula': formula,
    'priority': 0,
    'target': target['id'],
    'subTarget': subtarget,
    'modifier': type
  }
  return changes;
