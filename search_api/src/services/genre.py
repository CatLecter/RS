from models.genre import Genre, GenreBrief
from services.general import GeneralService


class GenreService(GeneralService):
    table = "genres"
    query_fields = ["name^5", "description"]
    item_dataclass = Genre
    item_brief_dataclass = GenreBrief
