FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc libpq-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY backend /app

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "nationalize.wsgi:application", "--bind", "0.0.0.0:8000"]
