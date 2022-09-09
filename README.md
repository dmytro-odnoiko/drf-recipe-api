# drf-reciepe-api

Core code of recipe-api based on Django Rest Framework project

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

If you haven't **docker** in machine, please install it before go on.

### 1. Setup project on local machine.

#### 1.1 Create and add env variable to project

Create **.env** file at the root folder of the project.

Define all variable from .env.example.
#### 1.2 Run project
Run **docker** containers:

For Linux/Mac OS: 
```bash
make start
```
For Windows:
```powerahell
docker-compose up
```
### 2. Project usage.
After running the project, open http://127.0.0.1:8000/api/docs and use Swagger UI to work with API. Prerequisites: create user with user API in Swagger page.Then get token for auth and add jwt token to authorize block. Now you can create, update and delete recipes. 

To get access to Django admin: create superuser(see command below) and login at http://127.0.0.1:8000/admin with your credentials to access to admin panel.
### 3. Some useful commands

#### 3.1 Docker
**Build app container via docker-compose:**

For Linux/Mac OS: 
```bash
make build
```
For Windows:
```powerahell
docker-compose build
```

**Build container without cache:**

For Linux/Mac OS: 
```bash
make build-nc
```
For Windows:
```powerahell
docker-compose build --no-cache
```

**Get access to app conrainer:**

For Linux/Mac OS: 
```bash
make exec-app
```
For Windows:
```powerahell
docker exec -ti drf-recipe-api_app_1 sh
```

**Get access to db conrainer**

For Linux/Mac OS: 
```bash
make exec-db
```
For Windows:
```powerahell
docker exec -ti drf-recipe-api_db_1 sh
```
#### 3.2 Testing and linting
**Run tests:**

For Linux/Mac OS: 
```bash
make test
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "python manage.py test"
```

**Run lining:**

For Linux/Mac OS: 
```bash
make linting
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "flake8"
```
#### 3.3 Django 
**Start Django app:**

For Linux/Mac OS: 
```bash
make APP_NAME=app_name startapp
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "python manage.py startapp app_name"
```

**Create Django migration:**

For Linux/Mac OS: 
```bash
make makemigrations
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

**Apply Django migration:**

For Linux/Mac OS: 
```bash
make migrate
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "python manage.py migrate"
```

**Run Django command:**

For Linux/Mac OS: 
```bash
make COMMAND=command manage-command
```
For Windows:
```powerahell
docker-compose run --rm app sh -c "python manage.py command"
```