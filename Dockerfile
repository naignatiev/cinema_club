FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt .

EXPOSE 8000
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get update \
    && apt-get install -y gettext

COPY . .
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
