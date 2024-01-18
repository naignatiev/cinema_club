import os
from contextlib import closing

from dotenv import load_dotenv
import psycopg2
from randomtimestamp import randomtimestamp


load_dotenv()

dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT')
}


if __name__ == '__main__':
    with closing(psycopg2.connect(**dsl)) as pg_conn, closing(pg_conn.cursor()) as cursor:
        cursor.execute(
            'select "id" from content.film_work'
        )
        uuids = cursor.fetchall()
        for uuid in uuids:
            cursor.execute(
                'update content.film_work set "creation_date"=%s where "id"=%s',
                (randomtimestamp(), uuid)
            )
        pg_conn.commit()
