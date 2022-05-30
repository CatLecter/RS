CREATE TABLE IF NOT EXISTS default.ratings (user_uuid UUID, movie_uuid UUID, datetime DateTime, rating Float32)
    ENGINE = MergeTree() ORDER BY datetime PARTITION BY toYYYYMM(datetime);
