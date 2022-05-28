CREATE TABLE IF NOT EXISTS language (
    user_uuid UUID,
    movie_id UUID,
    datetime DateTime,
    language_movie String,
    language_client String
) Engine = MergeTree
PARTITION BY toYYYYMM(datetime)
ORDER BY (movie_id, user_uuid, datetime);


CREATE TABLE IF NOT EXISTS language_queue (
    user_uuid UUID,
    movie_id UUID,
    datetime DateTime,
    language_movie String,
    language_client String
)
ENGINE = Kafka
SETTINGS    kafka_broker_list = 'rc1b-2n3od7kv12gki7j7.mdb.yandexcloud.net:9091',
            kafka_topic_list = 'language',
            kafka_group_name = 'clickhouse-language-group',
            kafka_format = 'JSONEachRow',
            kafka_skip_broken_messages = 5;


CREATE MATERIALIZED VIEW IF NOT EXISTS language_queue_mv TO language AS
    SELECT user_uuid, movie_id, datetime, language_movie, language_client
    FROM language_queue;
