FROM tiangolo/uvicorn-gunicorn-fastapi:python3.12

WORKDIR /src/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED  1

COPY requirements.txt requiremnts.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src /src