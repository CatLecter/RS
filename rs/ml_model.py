import json
from typing import List

import pandas as pd
from config import log_config
from lightfm import LightFM
from loguru import logger
from models import GenreBrief, MovieBrief, PersonalRecommendation, RatingEvent
from scipy.sparse import coo_matrix

logger.add(**log_config)


def prediction_all(data: tuple) -> List[PersonalRecommendation]:
    def filter_multiple_occure(data_to_filter: list, field: str) -> list:
        data_to_filter = sorted(data_to_filter, key=lambda d: d[field])
        result = []
        i = 0
        while i < len(data_to_filter) - 1:
            if data_to_filter[i][field] == data_to_filter[i + 1][field]:
                res = data_to_filter[i]
                while res[field] == data_to_filter[i + 1][field]:
                    if res['datetime'] < data_to_filter[i + 1]['datetime']:
                        res = data_to_filter[i + 1]
                    i += 1
                    if i == len(data_to_filter) - 1:
                        break
                result.append(res)
            else:
                result.append(data_to_filter[i])
                if i == len(data_to_filter) - 2:
                    result.append(data_to_filter[i + 1])
            i += 1
        if i == len(data_to_filter) - 1:
            result.append(data_to_filter[i])
        return result

    def create_matrix(dataset: pd.DataFrame, col_value: str, col1: str, col2: str,
                      col1_mapping: dict,
                      col2_mapping: dict):
        # Создадим разреженную матрицу рейтинга
        train_col1_data = dataset[col1].map(col1_mapping)
        train_col2_data = dataset[col2].map(col2_mapping)
        shape = (len(col1_mapping), len(col2_mapping))
        return coo_matrix(
            (dataset[col_value].values,
             (train_col1_data.astype(int), train_col2_data.astype(int))),
            shape=shape)

    def user_movie_columns(data_list: list) -> list:
        # Создаем список с колнками для датафрейма
        reslist = [[], [], []]
        for event in data_list:
            if not event['user_uuid'] in reslist[0]:
                reslist[0].append(event['user_uuid'])
                reslist[1].append(event['movie']['uuid'])
                reslist[2].append(event['rating'])
        return reslist


    def user_prediction(user_id, model, user_id_mapping, movie_numbers, movie_ids):
        # Предсказание для конкретного пользователя
        movie_nums = [i for i in range(0, movie_numbers)]
        prediction = model.predict(user_id_mapping[user_id], movie_nums)
        prediction_movie_id = list(zip(prediction, movie_ids))
        prediction_movie_id.sort()
        logger.info('Top 10 movies for user with user_id={} is {}'.format(user_id,
                                                                          prediction_movie_id[
                                                                          :10]))
        # return PersonalRecommendation(user_uuid=user_id, movies=[i[1] for i in prediction_movie_id[:10]])
        movies = tuple(i[1] for i in prediction_movie_id[:10])
        return {'user_uuid': user_id, 'movies': movies}

    bookmarks, ratings, views, watched = data
    logger.info('Принято {} записей о рейтинге, {} закладок'.format(len(ratings),len(bookmarks)))
    # Создаем матрицу user-movies
    # Оставляем только последние отметки

    a=set()
    for event in ratings:
        a.add(event['user_uuid'])
    logger.info('Уникальных пользователей {}'.format(len(a)))
    user_movie_rating = user_movie_columns(filter_multiple_occure(ratings, 'user_uuid'))
    logger.info('Отфильтровано {} записей о рейтинге'.format(len(user_movie_rating[0])))
    user_movie_rating_pd = pd.DataFrame(user_movie_rating,
                                        index=['user_id', 'movie_id', 'rating']).T
    user_id_mapping = {id: i for i, id in
                       enumerate(user_movie_rating_pd['user_id'].unique())}
    movie_ids = user_movie_rating_pd['movie_id'].unique()
    logger.debug('movie_ids', movie_ids[:3])
    movie_id_mapping = {id: i for i, id in enumerate(movie_ids)}
    user_movie_rating_matrix = create_matrix(user_movie_rating_pd, 'rating', 'user_id',
                                             'movie_id', user_id_mapping,
                                             movie_id_mapping)

    #Создаем матрицу item_features
    ...

    model = LightFM(loss='warp')
    model.fit(interactions=user_movie_rating_matrix, epochs=2,
              num_threads=2)
    movie_numbers = len(movie_id_mapping)
    result_list = []
    for user in user_id_mapping:
        res = user_prediction(user, model, user_id_mapping, movie_numbers, movie_ids)
        logger.debug('Выгружен {} '.format(res))
        result_list.append(res)
    logger.info('Выгружено {} рекомендаций'.format(len(result_list)))

    return json.dumps(result_list)
