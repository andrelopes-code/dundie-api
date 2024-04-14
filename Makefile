SHELL := /bin/bash

up:
	docker-compose up -d
	docker-compose logs api --follow


