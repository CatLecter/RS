---Создание базы данных фильмов:
CREATE DATABASE movies;

-- Создание схемы для контента:
CREATE SCHEMA IF NOT EXISTS content;

-- Установка uuid-ossp модуля для генерации UUID:
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание в схеме content таблицы с информацией о фильмах:
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Создание в схеме content таблицы с жанрами фильмов:
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Создание в схеме content таблицы с участниками фильмов:
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL UNIQUE,
    birth_date DATE,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

-- Создание в схеме content таблицы связи жанров и фильмов:
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    FOREIGN KEY (film_work_id)
        REFERENCES content.film_work (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (genre_id)
        REFERENCES content.genre (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    created_at timestamp with time zone
);

-- Создание в схеме content таблицы связи участников c фильмами:
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    FOREIGN KEY (film_work_id)
        REFERENCES content.film_work (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (person_id)
        REFERENCES content.person (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    role TEXT NOT NULL,
    created_at timestamp with time zone
);

-- Создание уникального композитного индекса для связи жанров и фильмов:
CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

-- Создание уникального композитного индекса для таблицы связи участников фильмов:
CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
