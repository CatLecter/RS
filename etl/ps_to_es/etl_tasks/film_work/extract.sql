SELECT film_work_id, MAX(updated_at) AS updated_at
FROM
    (
        SELECT id AS film_work_id, updated_at FROM film_work
        UNION (
            SELECT film_work_id, updated_at FROM genre JOIN genre_film_work ON genre.id = genre_id
        )
        UNION (
            SELECT film_work_id, updated_at FROM person JOIN person_film_work ON person.id = person_id
        )
    ) t
WHERE
    updated_at > %s
GROUP BY
    film_work_id
ORDER BY
    MAX(updated_at);
