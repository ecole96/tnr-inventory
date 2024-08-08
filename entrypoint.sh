#!/bin/sh

set -eu

. /scripts/inject_secrets.sh

# initialize db if it doesn't already exist
if [ ! -e "${DB_PATH}" ]
then
    echo "No database file detected at ${DB_PATH} - initializing one..."
    python /tnr-inventory/manage.py migrate
else
    echo "Database loaded at: ${DB_PATH}"
fi

# Collect static files
python /tnr-inventory/manage.py collectstatic --noinput

exec "$@"
