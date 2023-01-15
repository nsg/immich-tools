FROM docker.io/syncthing/syncthing

RUN apk add python3 py3-pip

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD src/ /app/

RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
