# Dockerfile

FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE slots_project.settings

WORKDIR /app

COPY requirements.txt /app/

# Installer les dépendances dans l'image Docker
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]