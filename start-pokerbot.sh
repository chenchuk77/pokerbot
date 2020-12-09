#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#echo $ROOT_DIR


echo "starting a pokerbot container ..."
#docker run --rm --name=pokerbot -d -v $(readlink -f app):/app chenchuk/pokerbot:1.0
docker run --rm --name=pokerbot -d -v ${ROOT_DIR}/app:/app chenchuk/pokerbot:1.0

echo "press ^C to stop the running log ... This does NOT stop pokerbot !"
echo "------------------------------------------------------------------"

docker logs -f pokerbot
