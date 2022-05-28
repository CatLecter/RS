CREATE TABLE IF NOT EXISTS views (
    user_uuid UUID,
    movie_uuid UUID,
    datetime DateTime,
    progress UInt32
) Engine = MergeTree
PARTITION BY toYYYYMM(datetime)
ORDER BY (movie_uuid, user_uuid, datetime);


CREATE TABLE IF NOT EXISTS views_queue (
    user_uuid UUID,
    movie_uuid UUID,
    datetime DateTime,
    progress UInt32
)
ENGINE = Kafka
SETTINGS    kafka_broker_list = 'rc1b-2n3od7kv12gki7j7.mdb.yandexcloud.net:9091',
            kafka_topic_list = 'views',
            kafka_group_name = 'clickhouse-views-group',
            kafka_format = 'JSONEachRow',
            kafka_skip_broken_messages = 5;


CREATE MATERIALIZED VIEW IF NOT EXISTS views_queue_mv TO views AS
    SELECT user_uuid, movie_uuid, datetime, progress
    FROM views_queue;
