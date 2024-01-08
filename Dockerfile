FROM python:3.10

WORKDIR /opt/app
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY config config
COPY movies movies
COPY manage.py /opt/app
COPY requirements.txt /opt/app
COPY .env /opt/app

EXPOSE 8000
RUN pip install -r requirements.txt
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
