#!/bin/bash

#
# This script call the dakara feeder for each karaoke folder
#

set -e

: ${DAKARA_SERVER_DIR:=/path/to/dakara-server}
: ${DAKARANEKO_DIR:=/path/to/dakaraneko}
: ${KARA_DIR:=/path/to/karaoke_folder/}

OPTIONS="--prune --append-only"

cd ${DAKARA_SERVER_DIR}/dakara_server

# Activate virtualenv (uncomment to use it)
# ACTIVATE_PATH=/home/user/.virtualenvs/virtualenv_name/bin/activate
# source ${ACTIVATE_PATH}

./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/music_parse.py --directory Wmusic
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/music_parse.py --directory CJKmusic
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/anime_parse.py --directory Anime
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/game_parse.py --directory Jeu
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/live_action_parse.py --directory Live\ action
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/cartoon_parse.py --directory Dessin\ animé
./manage.py feed $KARA_DIR $OPTIONS --parser $DAKARANEKO_DIR/auto_parse.py --directory Nouveau
./manage.py feed $KARA_DIR $OPTIONS --directory Autre

# Remove unused artists and works
./manage.py prune --artists --works
