import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FilmWorkType(models.TextChoices):
    MOVIE = "movie", _("Movie")
    TV_SHOW = "tv_show", _("TV Show")


class FilmWork(TimeStampedModel):
    title = models.CharField(
        _("Название"),
        max_length=255,
    )
    description = models.TextField(_("Описание"), blank=True)
    creation_date = models.DateField(_("Дата выхода"), blank=True)
    certificate = models.TextField(_("Сертификат"), blank=True)
    file_path = models.FileField(
        _("Файл"),
        upload_to="film_works/",
        blank=True,
    )
    rating = models.FloatField(
        _("Рейтинг"),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        blank=True,
    )
    type = models.CharField(
        _("Тип"),
        max_length=20,
        choices=FilmWorkType.choices,
    )
    genres = models.ManyToManyField(
        "Genre",
        through="GenreFilmWork",
        related_name="filmworks",
    )
    persons = models.ManyToManyField(
        "Person",
        through="PersonFilmWork",
        related_name="filmworks",
    )

    class Meta:
        verbose_name = _("Фильм")
        verbose_name_plural = _("Фильмы")
        db_table = '"content"."film_work"'

    def __str__(self):
        return f"{self.title}"


class Genre(TimeStampedModel):
    name = models.CharField(_("Жанр"), max_length=255)
    description = models.TextField(_("Описание"), blank=True)

    class Meta:
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")
        db_table = '"content"."genre"'

    def __str__(self):
        return f"{self.name}"


class Person(TimeStampedModel):
    full_name = models.CharField(_("Полное имя"), max_length=255, blank=False)
    birth_date = models.DateField(_("Дата рождения"), blank=True)

    class Meta:
        verbose_name = _("Участник")
        verbose_name_plural = _("Участники")
        db_table = '"content"."person"'

    def __str__(self):
        return f"{self.full_name}"


class GenreFilmWork(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    film_work_id = models.ForeignKey(
        "FilmWork",
        to_field="id",
        db_column="film_work_id",
        on_delete=models.CASCADE,
    )
    genre_id = models.ForeignKey(
        "Genre",
        to_field="id",
        db_column="genre_id",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["film_work_id", "genre_id"],
                name="film_work_genre",
            ),
        ]
        verbose_name = _("Жанр фильма")
        verbose_name_plural = _("Жанры фильмов")
        db_table = '"content"."genre_film_work"'

    def __str__(self):
        return f"{self.genre_id}"


class PersonRole(models.TextChoices):
    DIRECTOR = "director", _("Режисёр")
    PRODUCER = "producer", _("Продюссер")
    OPERATOR = "operator", _("Оператор")
    COMPOSER = "composer", _("Композитор")
    ACTOR = "actor", _("Актёр")
    WRITER = "writer", _("Сценарист")


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work_id = models.ForeignKey(
        "FilmWork",
        to_field="id",
        db_column="film_work_id",
        on_delete=models.CASCADE,
    )
    person_id = models.ForeignKey(
        "Person",
        to_field="id",
        db_column="person_id",
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        _("Должность"),
        max_length=60,
        choices=PersonRole.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["film_work_id", "person_id", "role"],
                name="film_work_person_role",
            ),
        ]
        verbose_name = _("Участник фильма")
        verbose_name_plural = _("Участники фильмов")
        db_table = '"content"."person_film_work"'

    def __str__(self):
        return f"{self.person_id}"
