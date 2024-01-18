FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt .
EXPOSE 8000
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

CMD ["uwsgi", "--ini", "uwsgi.ini"]
