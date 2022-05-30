CREATE TABLE IF NOT EXISTS default.views (user_uuid UUID, movie_uuid UUID, datetime DateTime, progress UInt32)
    ENGINE = MergeTree() ORDER BY datetime PARTITION BY toYYYYMM(datetime);
