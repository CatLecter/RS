CREATE TABLE IF NOT EXISTS default.bookmarks (user_uuid UUID, movie_uuid UUID, datetime DateTime, bookmarked INT1)
    ENGINE = MergeTree() ORDER BY datetime PARTITION BY toYYYYMM(datetime);
