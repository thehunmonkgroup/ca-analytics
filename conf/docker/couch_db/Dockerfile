# Pull base image
#FROM mongo
#FROM klaemo/couchdb
FROM couchdb

MAINTAINER Alek  <aleks.cc@gmail.com>

RUN apt-get update && apt-get install -y netcat && \
    rm -rf /var/lib/apt/lists/*

# Add sources
ADD ./conf/db_data /usr/src/app

RUN /usr/src/app/couchdb-import-data.sh
