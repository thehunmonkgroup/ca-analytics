# Ca Analytics

## Installation
```
$ cd ca-analytics
$ mkvirtualenv -p /usr/bin/python3 circling
$ workon circling
$ pip3 install -r conf/requirements.pip
```
Developing/testing this script will require you to have access to working 
CouchDB and MongoDB instances with seeded data.

To set up one with docker read [Docker.md](DOCKER.md).

## Usage
Assuming the databases are configured properly:
```
$ cd ca-analytics
$ workon circling
$ ./src/ca-analytics.py
```
