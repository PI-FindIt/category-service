from typing import Literal

import strawberry
from pydantic import BaseModel, computed_field


class CategoryModel(BaseModel):
    name: str

    @computed_field
    @property
    def friendly_name(self) -> str:
        return self.name.replace("-", " ").capitalize()


@strawberry.experimental.pydantic.input(model=CategoryModel, all_fields=True)
class CategoryInput:
    pass


@strawberry.type
class Category:
    name: str
    friendly_name: str

    @strawberry.field()
    async def children(self) -> list["Category"]:
        return await get_hierarchy("children", self.name)

    @strawberry.field()
    async def parents(self) -> list["Category"]:
        return await get_hierarchy("parents", self.name)


async def get_hierarchy(
    hierarchy: Literal["children", "parents"], name: str
) -> list[Category]:
    from src.crud import crud_category

    return [
        Category(**obj.model_dump())
        for obj in await crud_category.get_hierarchy(hierarchy, name)
    ]
