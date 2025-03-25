from src.crud.base import CRUDBaseNeo4j
from src.models.model import Category, CategoryBase


class CrudCategory(CRUDBaseNeo4j[Category, CategoryBase]):
    def __init__(self) -> None:
        super().__init__(model=Category)


crud_category = CrudCategory()
