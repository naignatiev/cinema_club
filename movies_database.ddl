CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title varchar(120) NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT not null,
    created timestamp with time zone not null,
    modified timestamp with time zone not null
);

CREATE TABLE IF NOT EXISTS content.genre(
    id uuid PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created timestamp with time zone not null,
    modified timestamp with time zone not null
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid primary key,
    full_name text not null,
    created timestamp with time zone not null,
    modified timestamp with time zone not null
);

create table if not exists content.genre_film_work (
    id uuid primary key,
    genre_id uuid not null references content.genre (id) on delete restrict,
    film_work_id uuid not null references content.film_work (id) on delete cascade,
    created timestamp with time zone not null,
    UNIQUE(genre_id, film_work_id)
);

create table if not exists content.person_film_work (
    id uuid primary key,
    person_id uuid not null references content.person (id) on delete restrict,
    film_work_id uuid not null references content.film_work(id) on delete restrict,
    role text,
    created timestamp with time zone not null,
    UNIQUE(person_id, film_work_id, role)
);
