SELECT
    id,
    updated_at
FROM
    genre
WHERE
    updated_at > %s;
