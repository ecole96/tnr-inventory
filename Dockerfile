FROM python:3.10.5-slim

WORKDIR /

# get packages
RUN apt-get update

# setup cron for scripts to run on schedule
RUN apt-get -y install cron
COPY cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cronjobs

RUN mkdir tnr-inventory
COPY requirements.txt tnr-inventory/requirements.txt
RUN pip install --no-cache-dir -r tnr-inventory/requirements.txt

ENV DB_PATH=/db/tnr-inventory.sqlite3
RUN mkdir db

COPY scripts scripts
RUN chmod +x scripts/*.sh

COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

WORKDIR /tnr-inventory
COPY inventory inventory
COPY static static
COPY tnr_inventory tnr_inventory
COPY manage.py manage.py

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]

CMD printenv >> /etc/environment && cron && echo "Starting application..." && python /tnr-inventory/manage.py runserver 0.0.0.0:5000
