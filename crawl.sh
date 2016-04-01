#!/bin/bash

if [ -d "logs" ]; then
 	echo 'Folder "logs" exists'
else
	mkdir logs
fi

#python crawler.py http://www.bbvaapimarket.com/
python main.py PRO

FILE=$(ls -r data | head -1)

if [ -f "data/$FILE" ]; then
 	echo 'file '$FILE' exist'
 	#python template.py $FILE
else
	echo 'No file to process'
fi

#PROJECT_ID=dev-center/raml
#TOKEN=iZ8f2RZkT5zLhEFaE1BA
#FILE_ID=s
#curl https://gitlab.digitalservices.es/api/v3/projects/333/repository/tree?private_token=$TOKEN -k

#curl -k https://gitlab.digitalservices.es/dev-center/raml/raw/develop/US_Security.raml?private_token=$TOKEN

#https://gitlab.digitalservices.es/dev-center/raml/raw/develop/US_Security.raml?private_token=iZ8f2RZkT5zLhEFaE1BA