FROM node:18 as frontend_builder

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm install

COPY . /app/

RUN npm run build

FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install -y ca-certificates fuse3 sqlite3

COPY --from=flyio/litefs:0.5 /usr/local/bin/litefs /usr/local/bin/litefs
COPY ./litefs.yml /etc/litefs.yml

RUN mkdir -p /code

WORKDIR /code

RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root --no-interaction
COPY . /code
COPY --from=frontend_builder /app/static/js/ /code/static/js/
COPY --from=frontend_builder /app/static/css/ /code/static/css/

ENV SECRET_KEY "non-secret-key-for-building-purposes"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]
# CMD ["daphne", "-b", "0.0.0.0", "splashcat.asgi:application"]
