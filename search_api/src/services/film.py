from typing import Optional

from engines.search.general import SearchParams
from models.film import Film, FilmBrief, FilmFilterType, FilmSortingType
from models.general import Page
from services.general import GeneralService


class FilmService(GeneralService):
    table = "movies"
    query_fields = ["title^3", "description"]
    item_dataclass = Film
    item_brief_dataclass = FilmBrief

    async def get_sorted_filtered(
        self,
        sort: Optional[FilmSortingType],
        filter_field: Optional[FilmFilterType],
        filter_value: str,
        page_number: int,
        page_size: int,
    ) -> Page[item_brief_dataclass]:
        """Возвращает список фильмов с фильтрацией и сортировкой."""
        sort_value = sort.value if sort else None
        filter_field_value = filter_field.value if filter_field else None
        cache_key = f"{self.table}:get_sorted_filtered(sort={sort_value},\
                    filter_field={filter_field_value},filter_value={filter_value},\
                    page_number={page_number},page_size={page_size}))"
        params = SearchParams(
            sort_field=sort_value,
            filter_field=filter_field_value,
            filter_value=filter_value,
            page_number=page_number,
            page_size=page_size,
        )

        search_results = await self.cache_engine.load_from_cache(cache_key)
        if not search_results:
            search_results = await self.search_engine.search(
                table=self.table, params=params
            )
            await self.cache_engine.save_to_cache(cache_key, search_results)

        data_page = Page(
            items=[self.item_brief_dataclass(**item) for item in search_results.items],
            total=search_results.total,
            page_number=page_number,
            page_size=page_size,
        )
        return data_page
