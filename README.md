# API of project "Foodgram".

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


###
Full API documentation is available at endpoint: ```redoc/```

## Examples of requests

- user registration *(POST)*
>api/v1/users/ 
>```json
>{
>  "email": "my_email",
>  "username": "my_username",
>  "first_name": "my_first_name",
>  "last_name": "my_last_name",
>  "password": "my_password"
>}
>```

- getting token *(POST)*
>/api/v1/auth/token/login/ 
>```json
>{
>  "password": "my_password",
>  "email": "my_email"
>}
>```

## Technology

Python 3.7

Django 2.2.28

Django REST framework 3.12.4

Djoser 2.1.0

## Launch

Create and activate virtual environment
```
py -3.7 -m venv venv

source venv/Scripts/activate
```

Install dependencies from requirements.txt file
```
pip install -r requirements.txt
```

Perform migrations
```
py manage.py migrate
```

Run project
```
py manage.py runserver 8008
```

Project available at http://127.0.0.1:8008/admin/

## Author

[NotMainCode](https://github.com/NotMainCode) (backend)