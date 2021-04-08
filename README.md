docker-machine inspect default | grep IPAddress

https://github.com/goktug97/NEAT

http://192.168.99.100:3000

TODO
- Increase population size
- Limit x,y
- Tune parameters

```bash
SERVER_PORT=3000 COMPOSE_PROJECT_NAME=test docker-compose -f servers/gulp/docker-compose.yaml up --build
docker kill $(docker ps -q)
echo "y" | docker container prune

sh train.sh
```
