#!/bin/bash

echo "Start CouchDB in background"
couchdb -b

echo "Checking if up..."
until nc -z localhost 5984; do sleep 0.1; done
echo "done"

cd /usr/src/app/
gunzip circleanywhere.couch.gz


DB_NAME="circleanywhere"
echo "Creating db ${DB_NAME}"
curl -X PUT http://127.0.0.1:5984/${DB_NAME}

ps aux

echo "Importing DB"
/usr/src/app/couchdb-backup.sh -r -d ${DB_NAME} -f ./circleanywhere.couch -H 127.0.0.1

#echo "Shutting down DB"
#couchdb -b
