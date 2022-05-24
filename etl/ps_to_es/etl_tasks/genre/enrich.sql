SELECT
    id,
    name,
    description,
    updated_at
FROM
    genre
WHERE
    genre.id = ANY( %s::uuid[] );
