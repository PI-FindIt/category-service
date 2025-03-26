from typing import Literal

import strawberry
from pydantic import BaseModel


class Category(BaseModel):
    name: str

    @property
    def friendly_name(self) -> str:
        return (
            self.name.replace("-", " ")
            .replace("en:", "")
            .replace("pt:", "")
            .capitalize()
        )


@strawberry.experimental.pydantic.input(model=Category, all_fields=True)
class CategoryInput:
    pass


@strawberry.type
class CategoryType:
    name: str

    @strawberry.field()
    async def children(self) -> list["CategoryType"]:
        return await get_hierarchy("children", self.name)

    @strawberry.field()
    async def parents(self) -> list["CategoryType"]:
        return await get_hierarchy("children", self.name)


async def get_hierarchy(
    hierarchy: Literal["children", "parents"], name: str
) -> list[CategoryType]:
    from src.crud import crud_category

    return [
        CategoryType(**obj.model_dump())
        for obj in await crud_category.get_hierarchy(hierarchy, name)
    ]
