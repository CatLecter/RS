from ..schemas.base import OrjsonBaseModel


class MovieProgressMessage(OrjsonBaseModel):
    progress: int
