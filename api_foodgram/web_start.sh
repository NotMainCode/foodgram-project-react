python manage.py migrate --no-input
gunicorn api_foodgram.wsgi:application --bind 0:8000
