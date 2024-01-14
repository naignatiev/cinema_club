docker run -d \
  --name postgres \
  -p 5432:5432 \
  -v /mnt/D/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=123qwe \
  -e POSTGRES_USER=app \
  -e POSTGRES_DB=movies_database  \
  postgres:13
