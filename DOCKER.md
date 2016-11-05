# Smarbuy with docker - manual tests (not production!!)

## Prerequisites

### Docker installation
Install docker according to your platform: https://docs.docker.com/engine/getstarted/step_one/

## Creating and running production image

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


## Starting server from testers image (database temporary)
Each time you execute this command a new container will be created. After stop container will be removed.
Database content is saved in container so all content will be removed too.
```
$ docker run -it --rm --name ca_analytics circle_anywhere/ca_host
```


## Starting server from stopped container
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

## Starting bash
Starting bash:
```
$ docker run -it --rm --name analyticsapp circle_anywhere/ca_host bash
```


## Attach with bash to running container
1. Check containers id:
```
$ docker ps

$ docker exec -it 25c84674a98e bash
```
