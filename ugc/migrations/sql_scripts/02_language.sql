CREATE TABLE IF NOT EXISTS default.language (
    user_uuid UUID,
    movie_id UUID,
    datetime DateTime,
    language_movie String,
    language_client String
) ENGINE = MergeTree() ORDER BY datetime PARTITION BY toYYYYMM(datetime);
