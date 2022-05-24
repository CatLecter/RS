from functools import lru_cache

from aioredis import Redis
from core import config
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from engines.cache.redis import RedisCacheEngine
from engines.search.elastic import ElasticSearchEngine
from fastapi import Depends
from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    redis_cache = RedisCacheEngine(redis, config.CACHE_TTL)
    elastic_search = ElasticSearchEngine(elastic)
    return FilmService(redis_cache, elastic_search)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    redis_cache = RedisCacheEngine(redis, config.CACHE_TTL)
    elastic_search = ElasticSearchEngine(elastic)
    return GenreService(redis_cache, elastic_search)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    redis_cache = RedisCacheEngine(redis, config.CACHE_TTL)
    elastic_search = ElasticSearchEngine(elastic)
    return PersonService(redis_cache, elastic_search)
