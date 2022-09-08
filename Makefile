# Define required macros here
SHELL = /bin/sh

build:
	docker-compose build

build-nc:
	docker-compose build --no-cache

start:
	docker-compose up

exec-app:
	docker exec -ti drf-recipe-api_app_1 sh

exec-db:
	docker exec -ti drf-recipe-api_db_1 sh

test:
	docker-compose run --rm app sh -c "python manage.py test"

linting: 
	docker-compose run --rm app sh -c "flake8"
	
startapp:
	docker-compose run --rm app sh -c "python manage.py startapp $(APP_NAME)"

makemigrations:
	docker-compose run --rm app sh -c "python manage.py makemigrations"

migrate:
	docker-compose run --rm app sh -c "python manage.py migrate"

manage-command:
	docker-compose run --rm app sh -c "python manage.py $(COMMAND)"