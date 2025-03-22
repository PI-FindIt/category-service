from src.crud.base import CRUDBaseNeo4j
from src.models.model import Category, CategoryBase


class CrudModel(CRUDBaseNeo4j[Category, CategoryBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Category)


crud_model = CrudModel()
