import json
import time

from es_utils import get_es_instance
from log_utils import get_logger
from pg_utils import PGFilmWorkEnricher, PGFilmWorkExtractor
from settings.settings import get_settings
from state import get_state

# from dotenv import load_dotenv
#
# load_dotenv(dotenv_path="../.env")

logger = get_logger("main")

if __name__ == "__main__":
    settings = get_settings()
    state = get_state()
    pg_extractor = PGFilmWorkExtractor()
    pg_enricher = PGFilmWorkEnricher()
    es = get_es_instance()

    while True:
        for etl_task in settings.etl_tasks:
            last_updated = state.get_state(
                etl_task.pg.table, "1000-01-01 00:00:00.000000 +0000"
            )
            data_chunks = pg_extractor.create_iterator(
                query=etl_task.pg.queries.extract.read_text(),
                last_updated=last_updated,
                chunk_size=etl_task.chunk_size,
            )
            for data_chunk in data_chunks:
                enriched_data_chunk = pg_enricher.get_enriched_data_chunk(
                    query=etl_task.pg.queries.enrich.read_text(),
                    data_chunk=data_chunk,
                    data_class=etl_task.data_class,
                )
                es_data = [
                    enriched_data.to_es() for enriched_data in enriched_data_chunk
                ]

                if not es.is_index_exist(etl_task.es.index):
                    index_mapping = json.load(etl_task.es.mapping.open())
                    index_settings = json.load(etl_task.es.settings.open())
                    es.create_index(etl_task.es.index, index_mapping, index_settings)
                success, errors = es.insert_chunk(es_data, etl_task.es.index)
                if not errors:
                    last_updated = data_chunk[-1].updated_at.strftime(
                        "%Y-%m-%d %H:%M:%S.%f %z"
                    )
                    logger.info(f"Успешно загружено записей в ElasticSearch: {success}")
                else:
                    logger.error(
                        "При загрузке записей в ElasticSearch возникли ошибки."
                    )
                    for error in errors:
                        logger.error(error)
            state.set_state(key=etl_task.pg.table, value=last_updated)

        logger.info(f"Цикл окончен, засыпаем на {settings.cycles_delay} секунд.")
        time.sleep(settings.cycles_delay)
