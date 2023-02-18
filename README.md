# Foodgram

![yamdb workflow](https://github.com/NotMainCode/foodgram-project-react/actions/workflows/yamdb_workflow.yaml/badge.svg)

## Description

Users can publish recipes, subscribe to publications of other users, 
add favorite recipes to "Favorites" and "Shopping List", 
as well as download a summary list of products (txt file) needed to cook one or more selected dishes.


Unauthorized users can:

- Create an account
- View recipes on homepage
- View individual recipe pages
- Filter recipes by tags

Authorized users can additionally:

- Log in with their username and password
- Log out
- Change your own password
- Create/edit/delete your own recipes
- View user pages
- Work with a personal favorites list: add recipes to it and delete them, view your favorites recipes page
- Work with a personal shopping list: add/remove any recipes,
upload a file with the number of necessary ingredients for recipes from the shopping list
- Subscribe to recipe authors' publications and cancel your subscription, view your subscriptions page

In the standard Django admin panel, the administrator can additionally:

- Change the password of any user
- Create/block/delete user accounts
- Edit/delete any recipes
- Add/remove/edit ingredients
- Add/remove/edit tags

### The project is temporarily available at the links:

[Foodgram](http://158.160.17.67/recipes)

[Foodgram Admin Site](http://158.160.17.67/admin)

[Foodgram API documentation](http://158.160.17.67/api/docs/redoc.html)

## Technology

Python 3.7

Django 2.2.28

Django REST framework 3.12.4

Djoser 2.1.0

Docker 23.0.0

Docker Compose 2.15.1

PostgreSQL 13.0-alpine

Nginx 1.21.3-alpine

GitHub Actions

### Triggers of GitHub Actions workflow
- ```push to any branch``` - running flake8 tests
- ```push to master branch``` - pushing the app image to the DockerHub repository, 
running project on remote server, sending Telegram message about the successful completion of the workflow.
Django app: collectstatic, migrate

## Launch

- Create secret repository variables ([documentation](https://docs.github.com/en/actions/learn-github-actions/variables#creating-configuration-variables-for-an-environment)).
```
DOCKER_USERNAME=<docker_username>
DOCKER_PASSWORD=<docker_password>
DOCKER_REPO=<docker_username>/<image name>
SERVER_HOST=<server_pub_ip>
SERVER_PASSPHRASE=<server_passphrase>
SERVER_USER=<username>
SSH_KEY=<--BEGIN OPENSSH PRIVATE KEY--...--END OPENSSH PRIVATE KEY--> # cat ~/.ssh/id_rsa
TELEGRAM_TO=<telegram_account_ID> # https://telegram.im/@userinfobot?lang=en
TELEGRAM_TOKEN=<telegram_bot_token> # https://t.me/botfather


- ENV_FILE variable value

DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=<database name>
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password> 
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=<Django_secret_key>
DOCKER_REPO=<docker_username>/<image name>
DOCKER_REPO_FRONTEND=<docker_username>/<image name>
SERVER_HOST=<server_pub_ip>
SERVER_URL=http://<server_pub_ip>/admin
```


- Copy *docker-compose.yml*, *nginx* files and *docs/* folder to the server.
```shell
scp <path_to_file>/docker-compose.yml <username>@<server_pub_ip>:/home/<username>
scp <path_to_file>/nginx.conf <username>@<server_pub_ip>:/home/<username>
scp -r <path_to_folder>/docs <username>@<server_pub_ip>:/home/<username>
```

- Connect to the server.
```shell
ssh <username>@<server_pub_ip>
```

Install [docker](https://docs.docker.com/engine/install/ubuntu/)
and [compose plugin](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually).
Follow the [steps after installing Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/).
###

After activation and successful completion of the GitHub Actions workflow,
the project is available at:

```http://<server_pub_ip>/``` ```http://<server_pub_ip>/admin/```

###

- Create superuser
```shell
docker compose exec web python manage.py createsuperuser
```

- Enter test data into the database
>docker compose exec web python manage.py loaddata dump.json
>```
>| Username  |  Email   | Password |
>|-----------|----------|----------|
>| User      | uu@uu.uu | foodgram |
>| AdminUser | au@au.au | foodgram |
>| SuperUser | su@su.su | foodgram |
>```

- Create a database dump
```shell
docker compose exec web python manage.py dumpdata > db_dump.json
```

## Author

[NotMainCode](https://github.com/NotMainCode) (backend, CI/CD)