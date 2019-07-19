#!/bin/sh

wget $(curl --silent https://api.github.com/repos/DakaraProject/dakara-server/releases/latest | grep browser_download_url | sed -e 's/^.*\": \"//' -e 's/\"$//') -O dakara-server.zip

unzip dakara-server.zip
rm dakara-server.zip
mv dakara-server* /dakara-server
