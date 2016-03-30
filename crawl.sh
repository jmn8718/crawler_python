#!/bin/bash

if [ -d "logs" ]; then
 	echo 'Folder "logs" exists'
else
	mkdir logs
fi

python crawler.py http://www.bbvaapimarket.com/

#cd data

#FILE=$(ls -r | head -1)

#python template.py $FILE
