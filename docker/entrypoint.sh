#!/bin/bash

if [ ! -f /db/db.sqlite3 ] ; then
  touch /db/db.sqlite3
fi
ln -s /db/db.sqlite3 /dakara-server/dakara_server/db.sqlite3

if [ "$1" == "install" ]; then
  /dakara-server/dakara_server/manage.py migrate
  /dakara-server/dakara_server/manage.py createsuperuser
  /dakara-server/dakara_server/manage.py createplayer
  /dakara-server/dakara_server/manage.py createtags /dakaraneko/config.yaml
  /dakara-server/dakara_server/manage.py createworktypes /dakaraneko/config.yaml
elif [ "$1" == "run" ]; then
  /dakaraneko/feed.sh
  /dakara-server/dakara_server/manage.py runserver 0.0.0.0:22222
fi
