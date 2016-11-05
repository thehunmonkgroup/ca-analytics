# Smarbuy with docker - manual tests (not production!!)

## Prerequisites

### Docker instalation
Install docker according to your platform: https://docs.docker.com/engine/getstarted/step_one/

## Creating testers image

First execution can take a few minutes:
```
$ docker build -t img_name -f conf/docker/server/Dockerfile .
```

as a result you should see something like this:
```
$ Successfully built 5f2537fe3e78
```


## Starting server from testers image (database temporary)
Each time you execute this command a new container will be created. After stop container will be removed.
Database content is saved in container so all content will be removed too.
```
$ docker run -it --rm --name analyticsapp img_name
```
` # TODO: img_name`


## Starting server from stopped container
1. find its id:

```
$ docker ps -a
$
$CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS               NAMES
$6b2464ba8b29        img_name            "python3 manage.py ru"   8 seconds ago       Exited (0) 3 seconds ago                       nauseous_morse
```

2. start container:
```
$ docker start -ia 6b2464ba8b29
```

## Starting bash
Starting bash:
```
$ docker run -it --rm --name analyticsapp img_name bash
```


## Attach with bash to running container
1. Check containers id:
```
$ docker ps

$ docker exec -it 25c84674a98e bash
```
