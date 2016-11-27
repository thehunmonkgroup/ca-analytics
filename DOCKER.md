# Setup of Circe Anywhere analytical script environment

Developing/testing this script will require you to have access to working CouchDB and MongoDB.
Below are instructions on how to build then with docker.

Firstly there are instructions on how to build **MongoDB** & **CouchDB** databases.
Then how to build the **test environment** to check scripts workings on 
_CentOS 6.8_ host.

At the end is Docker reference documentation on how to install it.

# Prerequisites
Documentation assumes that the project's root is in `~/repo/ca-analytics`. 
Change your paths accordingly.  

You will need to copy backups files to `~/repo/ca-analytics/conf/db_data`:
* `ca-analytics.log` - Logs for MongoDB
* `circleanywhere.couch` - Backup of CouchDB made via `couchdb-backup.sh`

**All docker command should be issued form projects root**
```
$ cd ~/repo/ca-analytics
```

## Creating and running MongoDB and CouchDB
> All backup/seeding files described in [Prerequisites](#prerequisites) should be already copied to designated directory.  

All work should be done by the script `start_environment.sh` which will build and run COuchDB and MongoDB images.
```
$ ~/repo/ca-analytics/conf/docker/start_environment.sh
```
The script should work even if you symlink to it.
> TODO: verify existence of backup/seed files for databases 

## Testing application under CentOS 6.8
To verify if script runs under the CentOS 6.8 by building the image with script source code.
This image needs CouchDB and MongoDB be accessible on your local machine on defeault ports.
First execution can take a few minutes:
```
$ docker build -t circle_anywhere/ca_host -f conf/docker/ca_host/Dockerfile .
```

Start the container with `--net="host"` for now (one need to have DBs up and running on local ports):
```
$ docker run -it --rm --net="host" --name ca_analytics circle_anywhere/ca_host

# -i, --interactive  Keep STDIN open even if not attached
# -t, --tty          Allocate a pseudo-TTY
# --rm               Automatically remove the container when it exits
# --net              Thanks to that container will see localhost open ports
```

#### Starting server from stopped container
1. find its id:

```
$ docker ps -a
$
$CONTAINER ID        IMAGE                   COMMAND                  CREATED             STATUS                     PORTS               NAMES
$6b2464ba8b29        circle_anywhere/ca_host  "python3 manage.py ru"   8 seconds ago       Exited (0) 3 seconds ago                       nauseous_morse
```

2. start container:
```
$ docker start -ia 6b2464ba8b29
```

#### Starting bash
Starting bash:
```
$ docker run -it --rm --name ca_analytics circle_anywhere/ca_host bash
```

#### Attach with bash to running container
1. Check containers id:
```
$ docker ps

$ docker exec -it 25c84674a98e bash
```

## Docker installation
Install docker according to your platform: https://docs.docker.com/engine/getstarted/step_one/
