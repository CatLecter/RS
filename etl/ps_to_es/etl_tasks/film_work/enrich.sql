SELECT
    film_work.id,
    film_work.title,
    film_work.rating,
    film_work.description,
    film_work.updated_at,
    ARRAY_AGG(DISTINCT genre.id || '<separator>' || genre.name)                                                  AS genres,
    ARRAY_AGG(DISTINCT person.id || '<separator>' || person.full_name || '<separator>' || person_film_work.role) AS persons
FROM
    film_work
    LEFT JOIN genre_film_work ON genre_film_work.film_work_id = film_work.id
    LEFT JOIN genre ON genre.id = genre_film_work.genre_id
    LEFT JOIN person_film_work ON person_film_work.film_work_id = film_work.id
    LEFT JOIN person ON person.id = person_film_work.person_id
WHERE
    film_work.id = ANY( %s::uuid[] )
GROUP BY
    film_work.id;
