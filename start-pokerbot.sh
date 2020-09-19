#!/bin/bash
echo "starting a pokerbot container ..."
docker run --rm --name=pokerbot -d -v $(readlink -f app):/app chenchuk/pokerbot:1.0

echo "press ^C to stop the running log ... This does NOT stop pokerbot !"
echo "------------------------------------------------------------------"

docker logs -f pokerbot
