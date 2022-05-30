CREATE TABLE IF NOT EXISTS default.watched (user_uuid UUID, watched_movie UUID, datetime DateTime, added INT1)
    ENGINE = MergeTree() ORDER BY datetime PARTITION BY toYYYYMM(datetime);
