#!/bin/bash

echo "#####################"
echo "       BASE"
echo "#####################"

./extract-races.py
./extract-classes.py
./extract-skills.py
./extract-feats.py
./extract-feats-racial.py
./extract-spells.py
#./extract-conditions.py

echo "#####################"
echo "       CLASSFEATURES"
echo "#####################"

./extract-classfeatures.py
./extract-classes-archetypes.py

#./extract-classfeatures-arcanes.py
#./extract-classfeatures-astuces.py
#./extract-classfeatures-decouvertes.py
#./extract-classfeatures-domaines.py
#./extract-classfeatures-exploits.py
#./extract-classfeatures-inquisitions.py
#./extract-classfeatures-jugements.py
#./extract-classfeatures-lignages.py
#./extract-classfeatures-maledictions.py
#./extract-classfeatures-malefices.py
#./extract-classfeatures-ordres.py
#./extract-classfeatures.py
#./extract-classfeatures-rages.py
#./extract-classfeatures-talents.py

echo "#####################"
echo "       EQUIPMENT"
echo "#####################"

./extract-equipment-weapons.py
./extract-equipment-armors.py
./extract-equipment.py

echo "#####################"
echo "       MAGIC ITEM"
echo "#####################"

./extract-magic-armors.py
./extract-magic-weapons.py
./extract-magic-rings.py
./extract-magic-scepters.py
./extract-magic-staffs.py
./extract-magic-objects.py

echo "#####################"
echo "       TRAITS"
echo "#####################"

./extract-races-traits-alternatifs.py
./extract-traits.py

