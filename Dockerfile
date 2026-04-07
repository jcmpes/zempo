FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

# 👇 instalar deps en el sistema (sin venv)
RUN uv pip install --system .

# copiar código Django
COPY work_tracker/ /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn work_tracker.wsgi:application --bind 0.0.0.0:8000 --workers 2"]