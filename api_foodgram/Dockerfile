FROM python:3.7-slim
LABEL maintainer="https://github.com/NotMainCode"
WORKDIR /app
RUN apt-get update && apt-get install curl --yes
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x wait-for-it.sh web_start.sh
RUN python manage.py collectstatic --no-input
