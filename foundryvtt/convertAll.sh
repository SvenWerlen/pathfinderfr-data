#!/bin/bash
echo "Convert armors..."
./convertArmors.py
echo "Convert classes..."
./convertClasses.py
echo "Convert feats..."
./convertFeats.py
echo "Convert magic..."
./convertMagic.py
echo "Convert spells..."
./convertSpells.py
echo "Convert weapons..."
./convertWeapons.py
echo "Convert equipment..."
./convertEquipment.py
echo "Done."
