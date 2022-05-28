CREATE TABLE IF NOT EXISTS watched (
    user_uuid UUID,
    watched_movie UUID,
    datetime DateTime,
    added Bool
) Engine = MergeTree
PARTITION BY toYYYYMM(datetime)
ORDER BY (watched_movie, user_uuid, datetime);


CREATE TABLE IF NOT EXISTS watched_queue (
    user_uuid UUID,
    watched_movie UUID,
    datetime DateTime,
    added Bool
)
ENGINE = Kafka
SETTINGS    kafka_broker_list = 'rc1b-2n3od7kv12gki7j7.mdb.yandexcloud.net:9091',
            kafka_topic_list = 'watched',
            kafka_group_name = 'clickhouse-watched-group',
            kafka_format = 'JSONEachRow',
            kafka_skip_broken_messages = 5;


CREATE MATERIALIZED VIEW IF NOT EXISTS watched_queue_mv TO watched AS
    SELECT user_uuid, watched_movie, datetime, added
    FROM watched_queue;
