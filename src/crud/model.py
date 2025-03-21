from src.crud.base import CRUDBase
from src.models.model import Model, ModelBase


class CrudModel(CRUDBase[Model, ModelBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Model)


crud_model = CrudModel()
