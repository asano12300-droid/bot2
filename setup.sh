#!/bin/bash

echo -n "setupする?[Y/N]: "
read yn

if [[ "$yn" == "Y" || "$yn" == "y" ]]; then
	bash setup/commands.sh
	bash setup/git.sh
else
	echo "またね"
fi
