FROM ghcr.io/immich-app/immich-cli:latest

RUN apk add python3 py3-pip 


ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD src/ /app/

WORKDIR /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
ENTRYPOINT []
