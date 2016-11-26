# Pull base image
FROM mongo

MAINTAINER Alek  <aleks.cc@gmail.com>

# Add sources
ADD ./conf/db_data/ /usr/src/app

CMD ["mongoimport", "--db", "circleanywhere", "--collection", "analytics", "--file",  "/usr/src/app/ca-analytics.log", "-h", "mongo_app"]

