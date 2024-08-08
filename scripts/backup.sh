#!/bin/sh

set -eu

BACKUP_DIR=/backups
mkdir -p "$BACKUP_DIR"

BACKUP_PATH="$BACKUP_DIR/$(date +'%Y%m%d%H%M%S').tnr-inventory.json"

python /tnr-inventory/manage.py dumpdata > "$BACKUP_PATH"
