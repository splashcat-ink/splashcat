# Splashcat's Architechture

## Django Backend

Splashcat's backend runs on Django 4.2. Templates are rendered by Django. Data is stored in Postgres using Django's
included ORM and Redis for tasks and Pub/Sub.

### Apps

Splashcat's backend consists of several Django apps.

- battles
- notifications
- splatnet_assets
- users

### Tasks

Splashcat uses Celery to run tasks. These tasks are stored in the `tasks.py` file in each app.

## Frontend

The frontend is normal HTML, with htmx and _hyperscript for dynamic elements. Most styles are Tailwind.css.

## Hosting

Splashcat is hosted on DigitalOcean App Platform, with Postgres and Redis being handled by DigitalOcean's managed
databases product.

### Costs

TODO