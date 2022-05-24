SELECT
    person.id,
    person.full_name,
    person.birth_date,
    person.updated_at,
    ARRAY_AGG(DISTINCT film_work.id || '<separator>' || film_work.title || '<separator>' || film_work.rating || '<separator>' || person_film_work.role) AS film_works
FROM
    person
    LEFT JOIN person_film_work ON person_film_work.person_id = person.id
    LEFT JOIN film_work ON film_work.id = person_film_work.film_work_id
WHERE
    person.id = ANY( %s::uuid[] )
GROUP BY
    person.id;
