python manage.py migrate
gunicorn api_foodgram.wsgi:application --bind 0:8000
