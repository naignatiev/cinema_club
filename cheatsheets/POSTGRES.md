```shell 
  docker run -d \
  --name postgres \
  -p 5432:5432 \
  -v /mnt/D/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=123qwe \
  -e POSTGRES_USER=app \
  -e POSTGRES_DB=movies_database  \
  postgres:13
```

```shell
  -- Устанавливаем расширения для генерации UUID
  CREATE EXTENSION "uuid-ossp";
  
  -- Генерируем данные в интервале с 1900 по 2021 год с шагом в час. В итоге сгенерируется 1060681 записей

  INSERT INTO content.film_work (id, title, type, creation_date, rating, created, modified) SELECT uuid_generate_v4(), 'some name', case when RANDOM() < 0.3 THEN 'movie' ELSE 'tv_show' END , date::DATE, floor(random() * 100), Now(), NOW()
  FROM generate_series(
    '1900-01-01'::DATE,
    '2021-01-01'::DATE,
    '1 hour'::interval
  ) date; 

```
