FROM python:3.12.0-bookworm

WORKDIR /app

COPY . .
RUN apt-get update && \
    apt-get install -y \
    supervisor
RUN pip install -r requirements.txt

EXPOSE 4999

ADD supervisor.conf /app/
ADD hallway-display.conf /app/
CMD supervisord -n -c supervisor.conf