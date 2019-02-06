eval $(docker-machine env clads-annotation-system)
docker-compose up -d --no-deps --build mainapp
