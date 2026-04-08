FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# copy .env in /app/.env
COPY .env ./

COPY pyproject.toml uv.lock ./

# install dependencies in system (no venv)
RUN uv pip install --system .

# copy django app code
COPY work_tracker/ /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn work_tracker.wsgi:application --bind 0.0.0.0:8000 --workers 2"]