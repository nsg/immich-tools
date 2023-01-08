FROM docker.io/library/python:3.11

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD src/ /app/

WORKDIR /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
