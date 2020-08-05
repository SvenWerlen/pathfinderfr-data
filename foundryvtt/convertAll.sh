#!/bin/bash


echo "Convert armors..."
./convertArmors.py
#echo "Convert bestiaire..."
#./convertBestiaire.py
echo "Convert classes..."
./convertClasses.py
echo "Convert equipment..."
./convertEquipment.py
echo "Convert feats..."
./convertFeats.py
echo "Convert features..."
./convertFeatures.py
echo "Convert magic..."
./convertMagic.py
echo "Convert magic armors..."
./convertMagicArmors.py
echo "Convert magic weapons..."
./convertMagicWeapons.py
echo "Convert races..."
./convertRaces.py
echo "Convert skills..."
./convertSkills.py
echo "Convert spells..."
./convertSpells.py
echo "Convert weapons..."
./convertWeapons.py
echo "Done."
