from src.crud.base import CRUDBaseNeo4j
from src.models.model import Category, CategoryBase, CategoryFilterModel


class CrudCategory(CRUDBaseNeo4j[Category, CategoryBase, CategoryFilterModel]):
    def __init__(self) -> None:
        super().__init__(model=Category)


crud_category = CrudCategory()
