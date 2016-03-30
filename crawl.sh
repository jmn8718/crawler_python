#!/bin/bash

if [ -d "logs" ]; then
 	echo 'Folder "logs" exists'
else
	mkdir logs
fi

python crawler.py http://www.bbvaapimarket.com/

FILE=$(ls -r data | head -1)

if [ -f "data/$FILE" ]; then
 	echo 'file '$FILE' exist'
 	#python template.py $FILE
else
	echo 'No file to process'
fi

