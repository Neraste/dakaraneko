# Docker image for Dakara server

Docker setup to manage the server, with automatic configuration and database feeding.

## System requirements

* Docker
* Docker-compose

## Building

Please note that these instructions assume that you already initialized this repository's submodules (see [the main README](../README.md) for more details)

From this directory, just build the image with compose:

```
docker-compose build
```

## Settings

The only thing that you should edit is the [docker-compose.yml](docker-compose.yml) file.

### Port setup

By default, the port that will be used to run the server on the host is `8080`.
To change it, you can edit the `ports` section with:

```
      - "WHATEVER_PORT:22222"
```

### Kara base folder

To set the folder in which you store your karas, you need to edit the `/path/to/kara/base` part in the `volumes` section with the actual path on your host.

### Server setup

Run the `install` command with compose from this directory to setup the server:

```
docker-compose run dakara install
```

You will be asked to choose the credentials for the server's superuser, then for the player's account, during the process.

## Server start

To start the server, simply start the container with compose from this directory:

```
docker-compose up
```

This will also manage the feeding of the database, so the first start might take a **very** long time depending on the number of karas you own.

To stop the server, simply type `^C` and wait for a bit.

