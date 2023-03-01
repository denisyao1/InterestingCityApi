FROM  python:3.10.10-slim-bullseye

WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0"]