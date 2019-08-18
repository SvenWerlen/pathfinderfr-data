#!/bin/bash

echo "#####################"
echo "       BASE"
echo "#####################"

./extract-feats.py

echo "#####################"
echo "       EQUIPMENT"
echo "#####################"

./extract-weapons.py
./extract-armors.py
./extract-equipment.py

echo "#####################"
echo "       MAGIC ITEM"
echo "#####################"

#./extract-magic-armors.py
#./extract-magic-weapons.py
#./extract-magic-rings.py
#./extract-magic-scepters.py
#./extract-magic-staffs.py
#./extract-magic-objects.py

echo "#####################"
echo "       TRAITS"
echo "#####################"

./extract-races-traits-alternatifs.py
./extract-traits.py

