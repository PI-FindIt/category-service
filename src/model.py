from typing import Literal, Optional

import strawberry
from pydantic import BaseModel, computed_field


class CategoryModel(BaseModel):
    name: str

    @computed_field
    @property
    def friendly_name(self) -> str:
        return self.name.replace("-", " ").capitalize()


@strawberry.experimental.pydantic.input(model=CategoryModel, all_fields=True)
class CategoryBase:
    pass


@strawberry.federation.type(keys=["name"])
class Category:
    name: str
    friendly_name: str

    @strawberry.field()
    async def children(self) -> list["Category"]:
        return await get_hierarchy("children", self.name)

    @strawberry.field()
    async def parents(self) -> list["Category"]:
        return await get_hierarchy("parents", self.name)

    @classmethod
    async def resolve_reference(cls, name: str) -> Optional["Category"]:
        from src.crud import crud_category

        category_model = await crud_category.get(name)
        return Category(**category_model.model_dump()) if category_model else None


async def get_hierarchy(
    hierarchy: Literal["children", "parents"], name: str
) -> list[Category]:
    from src.crud import crud_category

    return [
        Category(**obj.model_dump())
        for obj in await crud_category.get_hierarchy(hierarchy, name)
    ]
