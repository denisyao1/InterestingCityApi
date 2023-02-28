FROM  tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./.env  .

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0"]