from models.person import Person, PersonBrief
from services.general import GeneralService


class PersonService(GeneralService):
    table = "persons"
    query_fields = ["full_name"]
    item_dataclass = Person
    item_brief_dataclass = PersonBrief
