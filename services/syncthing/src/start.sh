#!/bin/sh

# Start syncthing
/bin/entrypoint.sh /bin/syncthing -home /var/syncthing/config &

cd /app
uvicorn main:app --host 0.0.0.0 --reload
