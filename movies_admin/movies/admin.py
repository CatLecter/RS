from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenresInlineAdmin(admin.TabularInline):
    model = GenreFilmWork
    extra = 0
    verbose_name = "Жанр"
    autocomplete_fields = ("genre_id",)


class PersonsInlineAdmin(admin.TabularInline):
    model = PersonFilmWork
    extra = 0
    verbose_name = "Участники"
    autocomplete_fields = ("person_id",)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
        "type",
    )
    list_filter = ("type",)
    search_fields = (
        "title",
        "description",
        "id",
    )
    fields = (
        "title",
        "description",
        "creation_date",
        "certificate",
        "file_path",
        "rating",
        "type",
    )
    ordering = ("title",)
    inlines = (
        GenresInlineAdmin,
        PersonsInlineAdmin,
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    fields = ("name", "description")
    ordering = ("name",)


@admin.register(Person)
class PerosnAdmin(admin.ModelAdmin):
    list_display = ("full_name", "birth_date")
    search_fields = ("full_name", "birth_date")
    fields = ("full_name", "birth_date")
    ordering = ("full_name",)
