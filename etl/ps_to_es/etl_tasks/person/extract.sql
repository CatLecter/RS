SELECT person_id, MAX(updated_at) AS updated_at
FROM
    (
        SELECT id AS person_id, updated_at FROM person
        UNION (
            SELECT person_id, updated_at FROM film_work JOIN person_film_work ON film_work.id = film_work_id
        )
    ) t
WHERE
    updated_at > %s
GROUP BY
    person_id
ORDER BY
    MAX(updated_at);
