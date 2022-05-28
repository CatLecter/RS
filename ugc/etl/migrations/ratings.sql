CREATE TABLE IF NOT EXISTS ratings (
    user_uuid UUID,
    movie_uuid UUID,
    datetime DateTime,
    rating Float32
) Engine = MergeTree
PARTITION BY toYYYYMM(datetime)
ORDER BY (movie_uuid, user_uuid, datetime);


CREATE TABLE IF NOT EXISTS ratings_queue (
    user_uuid UUID,
    movie_uuid UUID,
    datetime DateTime,
    rating Float32
)
ENGINE = Kafka
SETTINGS    kafka_broker_list = 'rc1b-2n3od7kv12gki7j7.mdb.yandexcloud.net:9091',
            kafka_topic_list = 'ratings',
            kafka_group_name = 'clickhouse-ratings-group',
            kafka_format = 'JSONEachRow',
            kafka_skip_broken_messages = 5;


CREATE MATERIALIZED VIEW IF NOT EXISTS ratings_queue_mv TO ratings AS
    SELECT user_uuid, movie_uuid, datetime, rating
    FROM ratings_queue;
