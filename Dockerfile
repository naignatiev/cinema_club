FROM python:3.10

WORKDIR /opt/app
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt .
EXPOSE 8000
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
