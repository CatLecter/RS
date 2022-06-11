import json
from typing import List

import pandas as pd
from config import log_config, mlconfig
from lightfm import LightFM
from loguru import logger
from models import GenreBrief, MovieBrief, PersonalRecommendation, RatingEvent
from scipy.sparse import coo_matrix

logger.add(**log_config)


def filter_multiple_occure(data_to_filter: list, field: str) -> list:
    """
    Удаляет повторяющиеся события из списка, оставляя только последнее по времени.

    @param data_to_filter: список событий
    @param field: поле, по которому будет проходить сжатие
    @return: сжатый список событий
    """
    data_to_filter.sort(key=lambda d: (d[field], d['movie']['uuid']))
    result = []
    i = 0
    while i < len(data_to_filter) - 1:
        if data_to_filter[i][field] == data_to_filter[i + 1][field] and \
            data_to_filter[i]['movie']['uuid'] == data_to_filter[i + 1]['movie'][
            'uuid']:
            res = data_to_filter[i]
            while res[field] == data_to_filter[i + 1][field] and res['movie'][
                'uuid'] == data_to_filter[i + 1]['movie']['uuid']:
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
                break
        i += 1
    if i == len(data_to_filter) - 1:
        result.append(data_to_filter[i])
    return result


def create_matrix(dataset: pd.DataFrame, col_value: str, col: str, row: str,
                  col_mapping: dict,
                  row_mapping: dict) -> coo_matrix:
    """
    Создадим разреженную матрицу рейтинга

    @param dataset: датафрейм отношений между двумя списками
    @param col_value: имя столбца с значениями
    @param col: имя столбца с будущими строками
    @param row: имя столбца с будущими колонками
    @param col_mapping: пронумерованный список названий
    @param row_mapping: пронумерованный список названий
    @return: разреженная матрица
    """
    train_col1_data = dataset[col].map(col_mapping)
    train_col2_data = dataset[row].map(row_mapping)
    shape = (len(col_mapping), len(row_mapping))
    return coo_matrix(
        (dataset[col_value].values,
         (train_col1_data.astype(int), train_col2_data.astype(int))),
        shape=shape, dtype=int)


def user_movie_columns(data_list: list, col1: str, col3: str) -> list:
    """
    Преобразуем список событий в список списков [[объект],[свойство],[значение]]
    для дальнейшего преобразования в датафрейм
    @param data_list: список событий
    @param col1: имя столбца с объектами
    @param col3: имя столбца с свойствами
    @return: список списков [[объект],[свойство],[значение]]
    """
    reslist = [[], [], []]
    check = []
    for event in data_list:
        if not {event[col1]: event['movie']['uuid']} in check:
            reslist[0].append(event[col1])
            reslist[1].append(event['movie']['uuid'])
            reslist[2].append(event[col3])
        check.append({event[col1]: event['movie']['uuid']})
    return reslist


def user_prediction(user_id, model, user_id_mapping, movie_ids,
                    movie_feature_matrix):
    """
    Предсказание для конкретного пользователя
    @param user_id: UUID пользователя
    @param model: рассчитанная модель для всех пользователей
    @param user_id_mapping: пронумерованный список UUID пользователей
    @param movie_ids: список UUID фильмов
    @param movie_feature_matrix: разреженная матрица свойств фильмов
    @return: словарь с UUID пользователя и списком UUID фильмов
    """
    movie_nums = [i for i in range(0, len(movie_ids))]
    prediction = model.predict(user_ids=user_id_mapping[user_id],
                               item_features=movie_feature_matrix,
                               item_ids=movie_nums)
    prediction_movie_id = list(zip(prediction, movie_ids))
    prediction_movie_id.sort()
    logger.info('Top 10 movies for user with user_id={} is {}'.format(user_id,
                                                                      prediction_movie_id[
                                                                      :10]))
    return {'user_uuid': user_id,
            'movies': tuple(i[1] for i in prediction_movie_id[:10])}


def enrich(pdd: pd.DataFrame, data_list: list, weight: int) -> pd.DataFrame:
    """
    Добавление в датафрейм рейтингов фильм-пользователь данных о закладках и просмотрах
    @param pdd: датафрейм пользователь-фильм-рейтинг
    @param data_list: список событий закладок и просмотров
    @param weight: вес
    @return: обогащенный датафрейм
    """
    data_list_filtered = filter_multiple_occure(data_list, 'user_uuid')
    for event in data_list_filtered:
        if not (event['movie']['uuid'] in pdd['movie_id'] and event[
            'user_uuid'] in pdd['user_id']):
            if 'added' in event:
                if event['added'] == True:
                    pd.concat([pdd, pd.Series({'user_id': event['user_uuid'],
                                               'movie_id': event['movie']['uuid'],
                                               'rating': weight})], axis=0,
                              ignore_index=True)
                else:
                    pd.concat([pdd, pd.Series({'user_id': event['user_uuid'],
                                               'movie_id': event['movie']['uuid'],
                                               'rating': weight - 2})], axis=0,
                              ignore_index=True)
            if 'bookmarked' in event:
                if event['bookmarked'] == True:
                    pd.concat([pdd, pd.Series({'user_id': event['user_uuid'],
                                               'movie_id': event['movie']['uuid'],
                                               'rating': weight})], axis=0,
                              ignore_index=True)
    return pdd


def movie_data_enrich(*args: list) -> tuple:
    """
    Создание списка фильм-жанр и списка жанров из событий
    @param *args: списки событий
    @return: кортеж из списка фильм-жанр и списка всех жанров
    """
    movie_genres = []
    genre_set = set()
    for events_list in args:
        for event in events_list:
            if event['movie']['genres']:
                for genre in event['movie']['genres']:
                    genre_set.add(genre)
                if not {'genre': event['movie']['genres'],
                        'movie': {'uuid': event['movie']['uuid']}} in movie_genres:
                    movie_genres.append({'genre': event['movie']['genres'],
                                         'movie': {'uuid': event['movie']['uuid']}})
    return (movie_genres, genre_set)


def create_item_feature_matrix(ratings, watched, bookmarks, movie_id_mapping):
    """
    Создание матрицы свойств фильмов
    @param ratings: списки событий ratings
    @param watched: списки событий watched
    @param bookmarks: списки событий bookmarks
    @param movie_id_mapping: пронумерованный список фильмов
    @return: разреженная матрица свойств фильмов
    """
    # Собираем данные о фильмах и жанрах из всех источников
    movie_genres, genres = movie_data_enrich(ratings, watched, bookmarks)
    genre_id_mapping = {genre: i for i, genre in enumerate(list(genres))}
    logger.info(
        "Количество фильмов {}, жанров {}".format(len(movie_genres), len(genres)))
    logger.info(
        "Количество фильмов по матрице {}".format(len(movie_id_mapping)))
    movie_genre_by_one = [{'movie': movie['movie'], 'genre': genre, 'exist': 1} for
                          movie in movie_genres for genre in movie['genre']]
    movie_genre_exist = user_movie_columns(movie_genre_by_one, 'genre', 'exist')
    print(len(movie_genre_exist[0]))
    movie_genre_exist_pd = pd.DataFrame(movie_genre_exist,
                                        index=['genre', 'movie', 'exist']).T
    movie_genre_exist_pd = movie_genre_exist_pd[['movie', 'genre', 'exist']]
    logger.debug(movie_genre_exist_pd.shape)
    logger.debug(movie_genre_exist_pd.head)

    return create_matrix(movie_genre_exist_pd, 'exist', 'movie',
                         'genre', movie_id_mapping,
                         genre_id_mapping)


def prediction_all(data: tuple) -> json:
    """
    Функция выдачи рекомендаций пользователям.

    @param data: кортеж из списков событий выставления рейтинга, добавления в закладки, просмотров
    @return: Преобразованный в JSON список рекомендация для каждого пользователя, который делал какие-то действия в системе
    """

    bookmarks, ratings, views, watched = data
    logger.info('Принято {} записей о рейтинге, {} закладок'.format(len(ratings),
                                                                    len(bookmarks)))
    # Создаем матрицу user-movies
    # Оставляем только последние отметки рейтинга
    user_movie_rating = user_movie_columns(filter_multiple_occure(ratings, 'user_uuid'),
                                           'user_uuid', 'rating')
    logger.info('Отфильтровано {} записей о рейтинге'.format(len(user_movie_rating[0])))
    # Преобразуем в dataframe user-movies
    user_movie_rating_pd = pd.DataFrame(user_movie_rating,
                                        index=['user_id', 'movie_id', 'rating']).T
    # Добавляем данные из bookmarked (нет рейтинга у фильма, но есть в закладках - добавляем рейтинг 6)
    user_movie_rating_pd = enrich(user_movie_rating_pd, bookmarks, mlconfig.brating)
    # Добавляем данные из watched (нет рейтинга у фильма, но фильм просмотрен до конца - добавляем рейтинг 7)
    user_movie_rating_pd = enrich(user_movie_rating_pd, watched, mlconfig.wrating)
    #Пронумерованный список UUID пользователей
    user_id_mapping = {id: i for i, id in
                       enumerate(user_movie_rating_pd['user_id'].unique())}
    #Список уникальных UUID фильмов
    movie_ids = user_movie_rating_pd['movie_id'].unique()
    #Пронумерованный список UUID фильмов
    movie_id_mapping = {id: i for i, id in enumerate(movie_ids)}
    user_movie_rating_matrix = create_matrix(user_movie_rating_pd, 'rating', 'user_id',
                                             'movie_id', user_id_mapping,
                                             movie_id_mapping)

    # Создаем матрицу item_features
    movie_feature_matrix = create_item_feature_matrix(ratings, watched, bookmarks,
                                                      movie_id_mapping)

    # Создаем модель
    model = LightFM(loss='warp')
    logger.info(
        "Параметры модели: размеры матрицы {} на {}".format(len(user_id_mapping),
                                                            len(movie_id_mapping)))
    model.fit(interactions=user_movie_rating_matrix, item_features=movie_feature_matrix,
              epochs=mlconfig.epochs,
              num_threads=mlconfig.num_threads)

    # Создаем рекомендации для каждого пользователя из списка
    result_list = []
    for user in user_id_mapping:
        res = user_prediction(user, model, user_id_mapping, movie_ids,
                              movie_feature_matrix)
        result_list.append(res)
    logger.debug('Выгружено {} рекомендаций'.format(len(result_list)))

    return json.dumps(result_list)
