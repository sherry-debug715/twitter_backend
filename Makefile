NAME = sherry/twitter

.PHONY: build up stop logs 

build: docker-build 
up: docker-compose-up 
stop: docker-compose-stop 
logs: docker-compose-logs 
enter: docker-enter-twitter

docker-build:
	docker build -t "${NAME}" .

docker-compose-up:
	docker-compose up -d

docker-compose-stop:
	docker-compose stop

docker-compose-logs:
	docker-compose logs --tail=100 -f

docker-enter-twitter:
	docker exec -it twitter bash