SHELL := /bin/bash

initialize:
	bash start.sh

up:
	docker compose up -d
	docker compose logs api --follow

down:
	docker compose down
