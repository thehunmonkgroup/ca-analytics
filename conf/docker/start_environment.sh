#!/bin/bash
# (c) 2016 Alek
# Last revised 26/11/2016
#  Info:
#  -------
#  Start CouchDB docker test image or build one

project_root="$(dirname "$(readlink -f "$0")")"

# Relative to this scripts' location
data_dir="/../db_data"

couch_db_container_name="couchdb_app"
couch_db_db_name="circleanywhere"
couch_db_backup_filename="circleanywhere.couch"

# If changed, fix Dockerfile of mongo_db also
mongo_db_container_name="mongo_app"

mongo_db_importer_name="mongo_importer_app"



run_couchdb(){
    docker rm ${couch_db_container_name} -f
    docker run -itd -p 5984:5984 --name "${couch_db_container_name}" couchdb
}

initialize_couchdb(){
    echo "Waiting for CouchDB to get up..."
    until curl -X GET http://127.0.0.1:5984/5984/_all_dbs &>/dev/null; do sleep 0.1; done

    echo "Creating DB \"${couch_db_db_name}\""
    curl -X PUT http://127.0.0.1:5984/${couch_db_db_name}

    echo "Pushing data to \"${couch_db_db_name}\""
    "${project_root}/${data_dir}/couchdb-backup.sh" -r -d "${couch_db_db_name}" -f "${project_root}/${data_dir}/${couch_db_backup_filename}" -H 127.0.0.1
}

run_mongodb(){
    docker rm ${mongo_db_container_name} -f
    docker rm ${mongo_db_importer_name} -f

    docker run -itd -p 27017:27017 --name ${mongo_db_container_name} mongo

}

initialize_mongodb(){
    echo "Creating importer image"
    echo docker build -t circle_anywhere/mongo_db -f "${project_root}/mongo_db/Dockerfile" "${project_root}/${data_dir}"
    docker build -t circle_anywhere/mongo_db -f "${project_root}/mongo_db/Dockerfile" "${project_root}/../../"

    docker run -it --rm --link ${mongo_db_container_name} --name ${mongo_db_importer_name} circle_anywhere/mongo_db
}

main(){
    run_couchdb
    initialize_couchdb

    run_mongodb
    initialize_mongodb
}

main



